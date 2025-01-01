import pytest
from botocore.stub import Stubber
from fastapi import Form
from fastapi.testclient import TestClient

from src.api import app
from src.routes.post_refresh_signin import cognito_client

test_client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("COGNITO_USER_POOL_ID", "us-east-1_123456789")
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "123456789")


@pytest.fixture(autouse=True, scope="function")
def cognito_stub():
    with Stubber(cognito_client) as cognito_stubber:
        yield cognito_stubber
        cognito_stubber.assert_no_pending_responses()


def test_handler_valid_event_refresh_signin(cognito_stub):
    cognito_stub.add_response(
        "initiate_auth",
        {
            "ChallengeName": "PASSWORD_VERIFIER",
            "Session": "my-session-super-secret",
            "ChallengeParameters": {},
            "AuthenticationResult": {
                "AccessToken": "my-super-secret-token",
                "ExpiresIn": 3600,
                "TokenType": "Bearer",
                "RefreshToken": "my-super-secret-refresh-token",
                "IdToken": "my-super-secret-id-token",
                "NewDeviceMetadata": {
                    "DeviceKey": "my-device",
                    "DeviceGroupKey": "my-device-group",
                },
            },
        },
        expected_params={
            "AuthFlow": "REFRESH_TOKEN_AUTH",
            "AuthParameters": {
                "REFRESH_TOKEN": "my-super-secret-refresh-token",
            },
            "ClientId": "123456789",
        },
    )

    response = test_client.post(
        "/refresh",
        data={"refresh_token": "my-super-secret-refresh-token"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {"message": "Token refreshed"},
    )


def test_handler_refreshes_refresh_token(cognito_stub):
    cognito_stub.add_response(
        "initiate_auth",
        {
            "ChallengeName": "PASSWORD_VERIFIER",
            "Session": "my-session-super-secret",
            "ChallengeParameters": {},
            "AuthenticationResult": {
                "AccessToken": "my-super-secret-token",
                "ExpiresIn": 3600,
                "TokenType": "Bearer",
                "RefreshToken": "my-new-secret-refresh-token",
                "IdToken": "my-super-secret-id-token",
                "NewDeviceMetadata": {
                    "DeviceKey": "my-device",
                    "DeviceGroupKey": "my-device-group",
                },
            },
        },
        expected_params={
            "AuthFlow": "REFRESH_TOKEN_AUTH",
            "AuthParameters": {
                "REFRESH_TOKEN": "my-super-secret-refresh-token",
            },
            "ClientId": "123456789",
        },
    )

    response = test_client.post(
        "/refresh",
        data={"refresh_token": "my-super-secret-refresh-token"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        200,
        {"message": "Token refreshed"},
    )


def test_handler_not_authorized(cognito_stub):
    cognito_stub.add_client_error(
        "initiate_auth",
        service_error_code="NotAuthorizedException",
    )

    response = test_client.post(
        "/refresh",
        data={"refresh_token": "my-super-secret-refresh-token"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        401,
        {"detail": "Invalid or expired refresh token"},
    )


def test_handler_invalid_refresh_token(cognito_stub):
    cognito_stub.add_client_error(
        "initiate_auth",
        service_error_code="UknownException",
    )

    response = test_client.post(
        "/refresh",
        data={"refresh_token": "my-super-secret-refresh-token"},
    )

    pytest.helpers.assert_responses_equal(
        response,
        400,
        {
            "detail": "An error occurred (UknownException) when calling the InitiateAuth operation: "
        },
    )
