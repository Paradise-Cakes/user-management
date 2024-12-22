import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from mangum import Mangum

from src.routes import (
    post_confirm_forgot_password,
    post_confirm_signup,
    post_forgot_password,
    post_logout,
    post_resend_confirmation_code,
    post_signin,
    post_signup,
)

app = FastAPI(title="Users API", version="1.0.0", root_path="/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post_confirm_forgot_password.router)
app.include_router(post_confirm_signup.router)
app.include_router(post_forgot_password.router)
app.include_router(post_logout.router)
app.include_router(post_resend_confirmation_code.router)
app.include_router(post_signin.router)
app.include_router(post_signup.router)


def lambda_handler(event, context):
    handler = Mangum(app, lifespan="on", api_gateway_base_path="/v1")
    return handler(event, context)
