import time
from json import loads

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
        response = self.dm_account_api.login_api.post_v1_account_login(
            json_data={
                'login': login,
                'password': password
            }
        )
        token = {
            'x-dm-auth-token': response.headers['x-dm-auth-token']
        }
        self.dm_account_api.account_api.set_headers(token)
        self.dm_account_api.login_api.set_headers(token)

    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }

        response = self.dm_account_api.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f'Пользователь не был создан {response.json()}'

        token = self.get_activation_token_by_login(login=login)
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, 'Пользователь не был активирован'
        return response

    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True
    ):
        json_data = {
            'login': login,
            'password': password,
            'rememberMe': remember_me,
        }

        response = self.dm_account_api.login_api.post_v1_account_login(json_data=json_data)
        assert response.status_code == 200, 'Пользователь не не смог авторизоваться'
        return response

    def change_registered_user_email(
            self,
            login: str,
            password: str,
            email: str
    ):
        email = f'{email}_1'
        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }

        response = self.dm_account_api.account_api.put_v1_account_email(json_data=json_data)
        assert response.status_code == 200, 'email не изменен'

        token = self.get_activation_token_by_email(login, email)
        assert token is not None, f'Токен для пользователя {login} не был получен'
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, 'Пользователь не был активирован'
        return response

    def reset_user_password(
            self,
            login: str,
            email: str
    ):
        json_data = {
            'login': login,
            'email': email
        }
        response = self.dm_account_api.account_api.post_v1_account_password(json_data=json_data)
        assert response.status_code == 200, 'Пароль не был сброшен'
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
            oldPassword: str,
            newPassword: str
    ):
        json_data = {
            "login": login,
            "token": token,
            "oldPassword": oldPassword,
            "newPassword": newPassword
        }
        response = self.dm_account_api.account_api.put_v1_account_password(json_data=json_data)
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
                print(user_data)
                # print(user_data['ConfirmationLinkUri'].split('/')[-1])
                token = user_data['ConfirmationLinkUri'].split('/')[-1]
        return token
