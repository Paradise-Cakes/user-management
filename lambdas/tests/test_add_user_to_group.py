import pytest
from botocore.stub import Stubber

from src.add_user_to_group.handler import client, lambda_handler
from tests.support import default_context

event = {"userPoolId": "us-east-1_123456789", "userName": "anthony.soprano@gmail.com"}


@pytest.fixture(autouse=True, scope="function")
def cognito_stub():
    with Stubber(client) as cognito_stubber:
        yield cognito_stubber
        cognito_stubber.assert_no_pending_responses()


def test_handler_add_user_to_group(cognito_stub):
    cognito_stub.add_response(
        "admin_add_user_to_group",
        {},
        expected_params={
            "UserPoolId": "us-east-1_123456789",
            "Username": "anthony.soprano@gmail.com",
            "GroupName": "users",
        },
    )
    result = lambda_handler(event, default_context)
    assert result == event


def test_handler_add_user_to_group_error(cognito_stub):
    cognito_stub.add_client_error(
        "admin_add_user_to_group",
        "ResourceNotFoundException",
        "User pool us-east-1_123456789 does not exist.",
        expected_params={
            "UserPoolId": "us-east-1_123456789",
            "Username": "anthony.soprano@gmail.com",
            "GroupName": "users",
        },
    )

    with pytest.raises(Exception) as e:
        lambda_handler(event, default_context)
