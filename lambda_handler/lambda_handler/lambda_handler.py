import json
import boto3
import os
import logging
import uuid
import time
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RETRY_COUNT = 3
RETRY_DELAY = 2

def lambda_handler(event, context):
    execution_id = str(uuid.uuid4())
    logger.info(f"Execution ID: {execution_id}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")

    ecs_client = boto3.client('ecs')

    required_env_vars = ['CLUSTER_NAME', 'TASK_DEFINITION', 'SUBNET_ID', 'SECURITY_GROUP_ID']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Missing environment variables: {', '.join(missing_vars)}"})
        }

    cluster_name = os.environ['CLUSTER_NAME']
    task_definition = os.environ['TASK_DEFINITION']
    subnet_id = os.environ['SUBNET_ID']
    security_group_id = os.environ['SECURITY_GROUP_ID']

    try:
        body = json.loads(event['body'])
        provider = body['name']
        meeting_id = body['meeting_id']
        host_access_token = body['host_access_token']

        logger.info(f"Provider Name: {provider}")
        logger.info(f"Meeting ID: {meeting_id}")
        logger.info(f"Host Access Token: {host_access_token}")
        
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        error_message = f"Invalid or missing parameters: {str(e)}"
        logger.error(error_message)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_message})
        }

    environment_variables = [
        {'name': 'PROVIDER', 'value': provider},
        {'name': 'MEETING_ID', 'value': meeting_id},
        {'name': 'HOST_ACCESS_TOKEN', 'value': host_access_token}
    ]

    attempt = 0
    while attempt < RETRY_COUNT:
        try:
            logger.info(f"Starting EC2 Bot (Attempt {attempt + 1})...")
            response = ecs_client.run_task(
                cluster=cluster_name,
                launchType='EC2',
                taskDefinition=task_definition,
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': [subnet_id],
                        'securityGroups': [security_group_id],
                        'assignPublicIp': 'ENABLED'
                    }
                },
                overrides={
                    'containerOverrides': [{
                        'name': 'bot-container',
                        'environment': environment_variables
                    }]
                }
            )
            task_arn = response['tasks'][0]['taskArn']
            logger.info(f"EC2 Bot started successfully. Task ARN: {task_arn}")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "EC2 Bot started successfully.",
                    "taskArn": task_arn
                })
            }
        except ClientError as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < RETRY_COUNT:
                time.sleep(RETRY_DELAY)

    error_message = "Error starting EC2 Bot after multiple attempts."
    logger.error(error_message)
    return {
        "statusCode": 500,
        "body": json.dumps({"error": error_message})
    }
