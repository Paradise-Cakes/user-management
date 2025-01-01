import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, Form, HTTPException, Response

from src.lib.aws_resources import get_cognito_app_client_id
from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context(log_event=True)
@router.post("/refresh", status_code=200, tags=["Authentication"])
def post_refresh_signin(
    response: Response,
    refresh_token: str = Form(...),
    cognito_app_client_id: str = Depends(get_cognito_app_client_id),
):
    try:
        auth_response = cognito_client.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": refresh_token},
            ClientId=cognito_app_client_id,
        )

        access_token = auth_response["AuthenticationResult"]["AccessToken"]
        new_refresh_token = auth_response["AuthenticationResult"].get(
            "RefreshToken", refresh_token
        )
        expires_in = auth_response["AuthenticationResult"]["ExpiresIn"]

        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=expires_in,
            secure=True,
            httponly=True,
            samesite="none",
        )

        # update the refresh token if a new one is returned
        refresh_token_expires_in = 30 * 24 * 60 * 60  # 30 days
        if new_refresh_token != refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                max_age=refresh_token_expires_in,
                secure=True,
                httponly=True,
                samesite="none",
            )

        return fastapi_gateway_response(
            200, response.headers, {"message": "Token refreshed"}
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NotAuthorizedException":
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )
        raise HTTPException(status_code=400, detail=str(e))
