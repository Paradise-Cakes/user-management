import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from fastapi import APIRouter, Form, HTTPException, Depends

from src.lib.response import fastapi_gateway_response
from src.lib.aws_resources import get_cognito_app_client_id

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context(log_event=True)
@router.post("/confirm_forgot_password", status_code=200, tags=["Authentication"])
def post_confirm_forgot_password(
    email: str = Form(...),
    code: str = Form(...),
    password: str = Form(...),
    cognito_app_client_id: str = Depends(get_cognito_app_client_id),
):
    logger.info(f"Confirming password reset for email {email}")

    try:
        cognito_client.confirm_forgot_password(
            ClientId=cognito_app_client_id,
            Username=email,
            ConfirmationCode=code,
            Password=password,
        )
        return fastapi_gateway_response(
            200, {}, {"message": f"Password reset for {email} successful"}
        )
    except ClientError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))
