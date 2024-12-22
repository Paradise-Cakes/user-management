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
@router.post("/resend_confirmation_code", status_code=200, tags=["Authentication"])
def post_resend_confirmation_code(
    email: str = Form(...),
    cognito_app_client_id: str = Depends(get_cognito_app_client_id),
):
    logger.info(f"Resending confirmation code to user with email {email}")
    try:
        response = cognito_client.resend_confirmation_code(
            ClientId=cognito_app_client_id,
            Username=email,
        )
        return fastapi_gateway_response(
            200, {}, {"message": "Confirmation code resent", **response}
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "UserNotFoundException":
            raise HTTPException(status_code=400, detail="User not found")
        if e.response["Error"]["Code"] == "LimitExceededException":
            raise HTTPException(
                status_code=400, detail="Limit exceeded, please try again later"
            )
        raise HTTPException(status_code=400, detail=str(e))
