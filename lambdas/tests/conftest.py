import json

import pytest

from src.api import app
from src.lib.aws_resources import get_cognito_app_client_id, get_cognito_user_pool_id


@pytest.helpers.register
def assert_response_equal(r1, r2):
    assert json.loads(r1.get("body")) == json.loads(r2.get("body"))
    assert r1.get("statusCode") == r2.get("statusCode")


@pytest.helpers.register
def assert_responses_equal(r1, status_code=None, r2=None, headers=None):
    assert (
        status_code or json or headers
    ), "You must assert one of: status_code, json, or headers"

    if status_code:
        assert r1.status_code == status_code

    if r2:
        assert r1.json() == r2


@pytest.fixture(autouse=True)
def override_aws_resources():
    app.dependency_overrides[get_cognito_app_client_id] = lambda: "123456789"
    app.dependency_overrides[get_cognito_user_pool_id] = lambda: "us-east-1_123456789"
    yield
    app.dependency_overrides.clear()
