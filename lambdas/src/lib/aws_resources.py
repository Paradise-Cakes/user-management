import os


def get_cognito_app_client_id():
    return os.environ.get("COGNITO_APP_CLIENT_ID")


def get_cognito_user_pool_id():
    return os.environ.get("COGNITO_USER_POOL_ID")
