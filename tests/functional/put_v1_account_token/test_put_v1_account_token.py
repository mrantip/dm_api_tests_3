import allure


@allure.suite("Тесты проверки метода PUT v1/account/token")
@allure.sub_suite("Активация пользователя")
def test_post_v1_account(
        account_helper,
        prepare_user
):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
