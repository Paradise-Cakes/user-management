import imaplib
import os

import boto3
import pytest
from dotenv import load_dotenv
from request_helper import RequestHelper

from lib.auth_utils import get_user_confirmation_code_from_email

load_dotenv()


@pytest.fixture(scope="session")
def api_url():
    local_port = os.getenv("LOCAL_PORT")

    if local_port:
        return f"http://localhost:{local_port}"

    return "https://users-dev-api.megsparadisecakes.com"


@pytest.fixture(scope="session")
def request_helper(api_url):
    return RequestHelper(api_url, {})


@pytest.fixture(scope="session")
def dynamodb_client():
    return boto3.client("dynamodb", region_name="us-east-1")


@pytest.fixture(scope="session")
def cognito_client():
    return boto3.client("cognito-idp", region_name="us-east-1")


@pytest.fixture(scope="function")
def email_client():
    email = os.environ.get("DEV_TEST_EMAIL")
    password = os.environ.get("DEV_TEST_EMAIL_PASSWORD")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email, password)
    mail.select("inbox")

    return {"client": mail, "email": email}


@pytest.fixture(scope="function")
def function_signup(cognito_client, cleanup_cognito_users):
    email = os.environ.get("DEV_TEST_EMAIL")
    password = os.getenv("DEV_EMAIL_PASSWORD")

    cognito_client.sign_up(
        ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
        Username=email,
        Password=password,
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "given_name", "Value": "John"},
            {"Name": "family_name", "Value": "Cena"},
        ],
    )
    cleanup_cognito_users.append(email)

    return {"email": email, "password": password}


@pytest.fixture(scope="function")
def function_signup_and_verification_code(email_client, function_signup):
    mail_client = email_client["client"]
    email = function_signup["email"]
    password = function_signup["password"]

    confirmation_code = get_user_confirmation_code_from_email(
        mail_client, "Welcome to Paradise Cakes!", "Your verification code is:"
    )

    return {
        "email": email,
        "password": password,
        "confirmation_code": confirmation_code,
    }


@pytest.fixture(scope="function")
def function_confirmed_account(
    cognito_client,
    function_signup_and_verification_code,
):
    email = function_signup_and_verification_code["email"]
    confirmation_code = function_signup_and_verification_code["confirmation_code"]

    cognito_client.confirm_sign_up(
        ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"),
        Username=email,
        ConfirmationCode=confirmation_code,
    )

    return {"email": email}


@pytest.fixture(scope="function")
def function_forgot_password_code(
    email_client, cognito_client, function_confirmed_account
):
    mail_client = email_client["client"]
    email = function_confirmed_account["email"]

    cognito_client.forgot_password(
        ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"), Username=email
    )

    reset_code = get_user_confirmation_code_from_email(
        mail_client, "Reset Your Password", "Your reset code is:"
    )

    return {"email": email, "reset_code": reset_code}


@pytest.fixture(scope="function")
def cleanup_cognito_users(cognito_client):
    users_to_cleanup = []
    yield users_to_cleanup

    for email in users_to_cleanup:
        try:
            cognito_client.admin_delete_user(
                UserPoolId=os.getenv("DEV_USER_POOL_ID"),
                Username=email,
            )
            print(f"Deleted test user: {email}")
        except Exception as e:
            print(f"Failed to delete user {email}: {e}")
            raise e
