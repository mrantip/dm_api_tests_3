import pprint

import requests
from json import loads


def test_post_v1_account():
    # Регистрация пользователя

    login = 'naruto_54'
    email = f'{login}@gmail.com'
    password = '123456789'

    json_data = {
        'login': login,
        'email': email,
        'password': password,
    }

    response = post_v1_account(json_data)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 201, f'Пользователь не был создан {response.json()}'

    # Получить письма из почтового сервера

    response = get_api_v2_messages(response)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Письма не были получены'

    # Получить активационный токен
    token = get_activation_token_by_login(login, response)

    assert token is not None, f'Токен для пользователя {login} не был получен'

    # Активация пользователя

    response = put_v1_account_token(token)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Пользователь не был активирован'

    # # Авторизоваться

    response = post_v1_account_login(login, password, response)
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200, 'Пользователь не не смог авторизоваться'


def post_v1_account_login(login, password, response):
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True,
    }
    response = requests.post('http://5.63.153.31:5051/v1/account/login', json=json_data)
    return response


def put_v1_account_token(token):
    headers = {
        'accept': 'text/plain',
    }
    response = requests.put(f'http://5.63.153.31:5051/v1/account/{token}', headers=headers)
    return response


def get_activation_token_by_login(login, response):
    token = None
    for item in response.json()['items']:
        user_data = loads(item['Content']['Body'])
        user_login = user_data['Login']
        if user_login == login:
            token = user_data['ConfirmationLinkUrl'].split('/')[-1]
    return token


def get_api_v2_messages(response):
    params = {
        'limit': '50',
    }
    response = requests.get('http://5.63.153.31:5025/api/v2/messages', params=params, verify=False)
    return response


def post_v1_account(json_data):
    response = requests.post('http://5.63.153.31:5051/v1/account', json=json_data)
    return response
