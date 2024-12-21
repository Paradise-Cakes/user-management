import os

import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import APIRouter, Form, HTTPException

from src.lib.response import fastapi_gateway_response

logger = Logger()
router = APIRouter()

load_dotenv()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context(log_event=True)
@router.post("/forgot_password", status_code=200, tags=["Authentication"])
def post_forgot_password(email: str = Form(...)):
    logger.info(f"Sending reset password request to email {email}")

    try:
        cognito_client.forgot_password(
            ClientId=os.environ.get("COGNITO_APP_CLIENT_ID"), Username=email
        )
        return fastapi_gateway_response(
            200, {}, {"message": f"Password reset email sent to {email}"}
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidParameterException":
            return fastapi_gateway_response(
                200, {}, {"message": f"Password reset email sent to {email}"}
            )
        raise HTTPException(status_code=400, detail=str(e))
