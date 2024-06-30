from datetime import datetime
from hamcrest import (
    all_of,
    assert_that,
    has_property,
    instance_of,
    starts_with,
)


class GetV1Account:
    @classmethod
    def check_response_values(
            cls,
            response
    ):
        assert_that(
            response, all_of(
                has_property('resource', has_property('login', starts_with('naruto'))),
                has_property('resource', has_property('online', instance_of(datetime)))
            )
        )
