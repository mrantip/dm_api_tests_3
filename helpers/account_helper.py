import time
from json import loads

from dm_api_account.models.change_email import ChangeEmail
from dm_api_account.models.change_password import ChangePassword
from dm_api_account.models.login_credentials import LoginCredentials
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_password import ResetPassword
from services.api_mailhog import MailHogApi
from services.dm_api_account import DMApiAccount
from retrying import retry


def retry_if_result_none(
        result
):
    """Return True if we should retry (in this case when result is None), False otherwise"""
    return result is None


def retrier(
        function
):
    def wrapper(
            *args,
            **kwargs
    ):
        token = None
        count = 0
        while token is None:
            print(f'Попытка получения токена номер {count}')
            token = function(*args, **kwargs)
            count += 1
            if count == 5:
                raise AssertionError('Превышено количество попыток получения активационного токена')
            if token:
                return token
            time.sleep(1)

    return wrapper


class AccountHelper:
    def __init__(
            self,
            dm_account_api: DMApiAccount,
            mailhog: MailHogApi
    ):
        self.dm_account_api = dm_account_api
        self.mailhog = mailhog

    def auth_client(
            self,
            login: str,
            password: str
    ):
        response = self.user_login(
            login=login,
            password=password
        )
        token = {
            'x-dm-auth-token': response.headers['x-dm-auth-token']
        }
        self.dm_account_api.account_api.set_headers(token)
        self.dm_account_api.login_api.set_headers(token)

    def get_current_user_info(
            self,
            **kwargs
    ):
        response = self.dm_account_api.account_api.get_v1_account(**kwargs)
        return response

    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        registration = Registration(
            login=login,
            email=email,
            password=password,
        )

        response = self.dm_account_api.account_api.post_v1_account(registration=registration)
        assert response.status_code == 201, f'Пользователь не был создан {response.json()}'
        start_time = time.time()
        token = self.get_activation_token_by_login(login=login)
        end_time = time.time()
        assert end_time - start_time < 3, 'Время ожидания активации превышено'
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        return response

    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True,
            validate_response=False,
            validate_headers=False
    ):
        login_credentials = LoginCredentials(
            login=login,
            password=password,
            remember_me=remember_me,
        )

        response = self.dm_account_api.login_api.post_v1_account_login(
            login_credentials=login_credentials, validate_response=validate_response
        )
        if validate_headers:
            assert response.headers['x-dm-auth-token'], 'Токен для пользователя не был получен'
            assert response.status_code == 200, 'Пользователь не не смог авторизоваться'
        return response

    def change_registered_user_email(
            self,
            login: str,
            password: str,
            email: str
    ):
        # email = f'{email}_1'
        change_email = ChangeEmail(
            login=login,
            password=password,
            email=email
        )

        response = self.dm_account_api.account_api.put_v1_account_email(change_email=change_email)
        # assert response.status_code == 200, 'email не изменен'

        token = self.get_activation_token_by_email(login, email)
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        # assert response.status_code == 200, 'Пользователь не был активирован'
        return response

    def reset_user_password(
            self,
            login: str,
            email: str
    ):
        reset_password = ResetPassword(
            login=login,
            email=email
        )
        response = self.dm_account_api.account_api.post_v1_account_password(reset_password=reset_password)
        # assert response.status_code == 200, 'Пароль не был сброшен'
        return response

    def get_token_for_change_user_password(
            self,
            login: str
    ):
        token = self.get_reset_token_by_login(login=login)
        assert token is not None, f"Токен для сброса пароля пользователя {login} не был получен"
        return token

    def change_user_password(
            self,
            login: str,
            token: str,
            old_password: str,
            new_password: str
    ):
        change_password = ChangePassword(
            login=login,
            token=token,
            old_password=old_password,
            new_password=new_password
        )
        response = self.dm_account_api.account_api.put_v1_account_password(change_password=change_password)
        assert response.status_code == 200, "Пароль не был изменён"

    def logout_current_user(
            self
    ):
        response = self.dm_account_api.login_api.delete_v1_account_login()
        assert response.status_code == 204, 'User не был разлогинен'
        return response

    def logout_user_from_all_devices(
            self
    ):
        response = self.dm_account_api.login_api.delete_v1_account_login()
        assert response.status_code == 204, 'User не был разлогинен со всех устройств'
        return response

    @retry(
        stop_max_attempt_number=5,
        retry_on_result=retry_if_result_none,
        wait_fixed=1000
    )
    def get_activation_token_by_login(
            self,
            login
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:
            user_data = loads(item['Content']['Body'])
            user_login = user_data['Login']
            if user_login == login:
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
        return token

    @retry(
        stop_max_attempt_number=5,
        retry_on_result=retry_if_result_none,
        wait_fixed=1000
    )
    def get_activation_token_by_email(
            self,
            login,
            email
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:
            user_data = loads(item['Content']['Body'])
            user_login = user_data['Login']
            user_email = item['Content']['Headers']['To'][0]
            if user_login == login and user_email == email:
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
        return token

    @retry(
        stop_max_attempt_number=5,
        retry_on_result=retry_if_result_none,
        wait_fixed=1000
    )
    def get_reset_token_by_login(
            self,
            login
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:
            user_data = loads(item['Content']['Body'])
            user_login = user_data['Login']
            if user_login == login:
                token = str(user_data.get('ConfirmationLinkUri')).split('/')[-1]
                break
        return token
