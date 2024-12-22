from src.api import app
from fastapi.testclient import TestClient

test_client = TestClient(app)


def test_confirm_forgot_password_success(setup_cognito_user_pool):
    response = test_client.post(
        "/confirm_forgot_password",
        data={
            "email": "anthony.soprano@gmail.com",
            "code": "123456",
            "password": "NewStrongPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Password reset for anthony.soprano@gmail.com successful"
    }
