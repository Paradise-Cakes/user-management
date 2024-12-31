import boto3
from aws_lambda_powertools import Logger

client = boto3.client("cognito-idp")
logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    user_pool_id = event["userPoolId"]
    username = event["userName"]

    try:
        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName="users",
        )
        logger.info(f"User {username} added to group users")
    except Exception as e:
        logger.error(f"Error adding user to group: {str(e)}")
        raise e

    return event
