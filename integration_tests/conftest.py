import os
import pytest

from moto import cognitoidp as mock_cognitoidp
import boto3


@pytest.fixture(scope="function", autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("COGNITO_USER_POOL_ID", "test_user_pool_id")
    monkeypatch.setenv("COGNITO_REGION", "us-east-1")


@pytest.fixture(scope="function")
def setup_cognito_user_pool():
    with mock_cognitoidp():
        cognito_client = boto3.client("cognito-idp", region_name="us-east-1")

        user_pool_response = cognito_client.create_user_pool(
            PoolName="test_user_pool",
            Policies={
                "PasswordPolicy": {
                    "MinimumLength": 8,
                    "RequireUppercase": True,
                    "RequireLowercase": True,
                    "RequireNumbers": True,
                    "RequireSymbols": True,
                }
            },
        )
        user_pool_id = user_pool_response["UserPool"]["Id"]

        user_pool_client_response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName="test-client",
        )
        client_id = user_pool_client_response["UserPoolClient"]["ClientId"]

        os.environ["COGNITO_APP_CLIENT_ID"] = client_id

        cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username="anthony.soprano@gmail.com",
            UserAttributes=[{"Name": "email", "Value": "anthony.soprano@gmail.com"}],
            TemporaryPassword="TempPass123!",
        )

        cognito_client.forgot_password(
            ClientId=client_id,
            Username="anthony.soprano@gmail.com",
        )

        yield cognito_client
