import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from fastapi import APIRouter, Form, Depends
from fastapi.exceptions import HTTPException

from src.lib.response import fastapi_gateway_response
from src.lib.aws_resources import get_cognito_app_client_id

logger = Logger()
router = APIRouter()

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")


@logger.inject_lambda_context(log_event=True)
@router.post("/signup", status_code=201, tags=["Authentication"])
def post_signup(
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    cognito_app_client_id: str = Depends(get_cognito_app_client_id),
):
    logger.info(f"Creating user with email {email}")

    try:
        response = cognito_client.sign_up(
            ClientId=cognito_app_client_id,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "given_name", "Value": first_name},
                {"Name": "family_name", "Value": last_name},
            ],
        )
        return fastapi_gateway_response(
            201,
            {},
            {
                "message": "User created",
                "email": email,
                "given_name": first_name,
                "family_name": last_name,
                **response,
            },
        )
    except ClientError as e:
        logger.error(str(e))
        if e.response["Error"]["Code"] == "UsernameExistsException":
            raise HTTPException(
                status_code=400, detail="User already exists with that email"
            )
        if e.response["Error"]["Code"] == "InvalidPasswordException":
            raise HTTPException(
                status_code=400,
                detail="Password must have uppercase, lowercase, number, special character, and be at least 8 characters long",
            )
        raise HTTPException(status_code=400, detail=str(e))
