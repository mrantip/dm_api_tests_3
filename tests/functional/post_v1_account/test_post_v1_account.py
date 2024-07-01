from datetime import datetime

import pytest
from hamcrest import (
    assert_that,
    has_property,
    starts_with,
    all_of,
    instance_of,
    has_properties,
    equal_to,
)

from checkers.http_checkers import check_status_code_http


def test_post_v1_account(
        account_helper,
        prepare_user
):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    response = account_helper.user_login(login=login, password=password, validate_response=True)
    assert_that(
        response, all_of(
            has_property('resource', has_property('login', starts_with('naruto'))),
            has_property('resource', has_property('registration', instance_of(datetime))),
            has_property(
                'resource', has_properties(
                    {
                        'rating': has_properties(
                            {
                                "enabled": equal_to(True),
                                "quality": equal_to(0),
                                "quantity": equal_to(0)
                            }
                        )
                    }
                )
            )
        )
    )


@pytest.mark.parametrize(
    'login, email, password, expected_status_code, error_message, ', [
        ('naruto_6_2', 'naruto_6_2@mail.ru', '111', 400, 'Validation failed'),  # Short password
        ('naruto_6_2', 'naruto_6_2%mail.ru', '123456789', 400, 'Validation failed'),  # Invalid email
        ('n', 'naruto_6_2@mail.ru', '123456789', 400, 'Validation failed')]# Invalid email
)
def test_post_v1_account_negative(
        account_helper,
        login,
        email,
        password,
        expected_status_code,
        error_message
):
    with check_status_code_http(expected_status_code, error_message):
        account_helper.register_new_user(login=login, password=password, email=email)
