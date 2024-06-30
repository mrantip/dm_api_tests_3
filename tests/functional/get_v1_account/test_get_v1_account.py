from checkers.get_v1_account import GetV1Account
from checkers.http_checkers import check_status_code_http


def test_get_v1_account_auth(
        account_helper,
        prepare_user
):
    with check_status_code_http():
        login = prepare_user.login
        password = prepare_user.password
        email = prepare_user.email
        account_helper.register_new_user(login=login, password=password, email=email)
        account_helper.user_login(login=login, password=password)
        account_helper.auth_client(login=login, password=password)
        response = account_helper.get_current_user_info(validate_response=True)
        GetV1Account.check_response_values(response)


# def test_get_v1_account_noauth(
#         account_helper
# ):
#     with check_status_code_http(401, 'User must be authenticated'):
#         account_helper.dm_account_api.account_api.get_v1_account()
