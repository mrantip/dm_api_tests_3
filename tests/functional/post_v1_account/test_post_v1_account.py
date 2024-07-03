import allure
import pytest

from checkers.http_checkers import check_status_code_http

from checkers.post_v1_account import PostV1Account


@allure.suite("Тесты на проверку метода POST v1/account")
@allure.sub_suite("Позитивные тесты")
class TestsPostV1Account:
    @allure.title("Проверка метода регистрации пользователя")
    def test_post_v1_account(
            self,
            account_helper,
            prepare_user
    ):
        login = prepare_user.login
        password = prepare_user.password
        email = prepare_user.email
        account_helper.register_new_user(login=login, password=password, email=email)
        response = account_helper.user_login(login=login, password=password, validate_response=True)
        PostV1Account.check_response_values(response)


    @allure.sub_suite("Негативные проверки")
    @allure.title("Проверка регистрации пользователя с невалидными данными")
    @pytest.mark.parametrize(
        'login, email, password, expected_status_code, error_message, ', [
            ('naruto_6_2', 'naruto_6_2@mail.ru', '111', 400, 'Validation failed'),  # Short password
            ('naruto_6_2', 'naruto_6_2%mail.ru', '123456789', 400, 'Validation failed'),  # Invalid email
            ('n', 'naruto_6_2@mail.ru', '123456789', 400, 'Validation failed')]  # Invalid login
    )
    def test_post_v1_account_negative(
            self,
            account_helper,
            login,
            email,
            password,
            expected_status_code,
            error_message
    ):
        with check_status_code_http(expected_status_code, error_message):
            account_helper.register_new_user(login=login, password=password, email=email)
