import random
from json import loads

from dm_api_account.apis.account_api import AccountApi
from dm_api_account.apis.login_api import LoginApi
from api_mailhog.apis.mailhog_api import MailhogApi
from tests.functional.post_v1_account.test_post_v1_account import get_activation_token_by_login


def test_post_v1_account():
    # Регистрация пользователя
    account_api = AccountApi(host='http://5.63.153.31:5051')
    login_api = LoginApi(host='http://5.63.153.31:5051')
    mailhog_api = MailhogApi(host='http://5.63.153.31:5025')

    login = f'naruto_{random.randint(1, 1000)}'
    email = f'{login}@gmail.com'
    password = '123456789'
    new_email = f'{login}_1@gmail.com'

    json_data = {
        'login': login,
        'email': email,
        'password': password,
    }

    response = account_api.post_v1_account(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 201, f'Пользователь не был создан {response.json()}'

    # Получить письма из почтового сервера

    response = mailhog_api.get_api_v2_messages()
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Письма не были получены'

    # Получить активационный токен
    token = get_activation_token_by_login(login, response)

    assert token is not None, f'Токен для пользователя {login} не был получен'

    # Активация пользователя

    response = account_api.put_v1_account_token(token=token)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Пользователь не был активирован'

    # Авторизоваться
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }

    response = login_api.post_v1_account_login(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Пользователь не смог авторизоваться'

    # Изменить email

    json_data_2 = {
        'login': login,
        'email': new_email,
        'password': password,
    }

    response = account_api.put_v1_account_email(json_data=json_data_2)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'email не изменен'

    # Пытаемся авторизоваться по новому email

    response = login_api.post_v1_account_login(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 403, 'Пользователь смог авторизоваться'

    # Получить письма из почтового сервера

    response = mailhog_api.get_api_v2_messages()
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Письма не были получены'

    # Получить активационный токен по новому email
    token = get_activation_token_by_email(login, new_email, response)
    assert token is not None, f'Токен для пользователя {login} не был получен'

    # Активация пользователя по новому токену

    response = account_api.put_v1_account_token(token=token)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Пользователь не был активирован'

    # Авторизоваться по новому email

    response = login_api.post_v1_account_login(json_data=json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Пользователь не не смог авторизоваться'


def get_activation_token_by_email(
        login,
        new_email,
        response
):
    token = None
    for item in response.json()['items']:
        user_data = loads(item['Content']['Body'])
        user_login = user_data['Login']
        user_email = item['Content']['Headers']['To'][0]
        if user_login == login and user_email == new_email:
            token = user_data['ConfirmationLinkUrl'].split('/')[-1]
    return token
