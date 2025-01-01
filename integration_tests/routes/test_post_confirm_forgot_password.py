from src.api import app
from fastapi.testclient import TestClient

test_client = TestClient(app)


def test_post_v1_confirm_forgot_password_returns_200(setup_cognito_user_pool):
    valid_code = setup_cognito_user_pool["valid_code"]

    response = test_client.post(
        "/v1/confirm_forgot_password",
        data={
            "email": "anthony.soprano@gmail.com",
            "code": valid_code,
            "password": "NewStrongPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Password reset for anthony.soprano@gmail.com successful"
    }


def test_post_v1_confirm_forgot_password_returns_400(setup_cognito_user_pool):
    response = test_client.post(
        "/v1/confirm_forgot_password",
        data={
            "email": "anthony.viera@gmail.com",
            "code": "WRONG_CODE",
            "password": "NewStrongPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "An error occurred (CodeMismatchException) when calling the ConfirmForgotPassword operation: Invalid code provided, please request a code again."
    }
