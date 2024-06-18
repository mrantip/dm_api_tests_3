def test_post_v1_account_email(
        account_helper,
        prepare_user
):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    new_email = prepare_user.new_email
    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.user_login(login=login, password=password)

    # Изменить email + активация
    account_helper.change_registered_user_email(login=login, password=password, email=new_email)

    # Авторизоваться после изменения email
    account_helper.user_login(login=login, password=password)
