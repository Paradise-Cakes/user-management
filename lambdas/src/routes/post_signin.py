import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, Form, HTTPException, Response

from src.lib.aws_resources import get_cognito_app_client_id
from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


def get_user_info(access_token):
    try:
        response = cognito_client.get_user(AccessToken=access_token)
        user_attributes = response["UserAttributes"]
        user_info = {attr["Name"]: attr["Value"] for attr in user_attributes}
        return user_info
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))


@logger.inject_lambda_context(log_event=True)
@router.post("/signin", status_code=200, tags=["Authentication"])
def post_signin(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    cognito_app_client_id: str = Depends(get_cognito_app_client_id),
):
    try:
        auth_response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
            ClientId=cognito_app_client_id,
        )

        access_token = auth_response["AuthenticationResult"]["AccessToken"]
        refresh_token = auth_response["AuthenticationResult"]["RefreshToken"]
        expires_in = auth_response["AuthenticationResult"]["ExpiresIn"]

        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=expires_in,
            secure=False,
            httponly=True,
            samesite="none",
        )

        refresh_token_expires_in = 30 * 24 * 60 * 60  # 30 days
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=refresh_token_expires_in,
            secure=False,
            httponly=True,
            samesite="none",
        )

        user_info = get_user_info(access_token)

        return fastapi_gateway_response(
            200, response.headers, {"message": "User signed in", **user_info}
        )
    except ClientError as e:
        if (
            e.response["Error"]["Code"] == "UserNotFoundException"
            or e.response["Error"]["Code"] == "NotAuthorizedException"
        ):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        if e.response["Error"]["Code"] == "UserNotConfirmedException":
            raise HTTPException(
                status_code=400,
                detail="User is not confirmed",
            )
        raise HTTPException(status_code=400, detail=str(e))
