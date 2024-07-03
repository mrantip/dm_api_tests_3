import allure


@allure.suite("Тесты проверки метода DELETE v1/account/login")
def test_delete_v1_account_login(
        account_helper,
        prepare_user
):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.user_login(login=login, password=password)
    account_helper.auth_client(login=login, password=password)
    account_helper.logout_current_user()
