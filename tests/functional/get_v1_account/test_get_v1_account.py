def test_get_v1_account_auth(
        account_helper,
        prepare_user
):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.user_login(login=login, password=password)
    account_helper.reset_user_password(login=login, email=email)
    account_helper.auth_client(login=login, password=password)
    account_helper.get_current_user_info()


def test_get_v1_account_noauth(
        account_helper
):
    account_helper.dm_account_api.account_api.get_v1_account()

