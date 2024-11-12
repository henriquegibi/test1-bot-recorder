import json
import boto3
import os
import logging
import uuid
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

    try:
        logger.info("Starting Fargate task...")
        response = ecs_client.run_task(
            cluster=cluster_name,
            launchType='FARGATE',
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
        logger.info(f"Fargate task started successfully. Task ARN: {task_arn}")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Fargate task started successfully.",
                "taskArn": task_arn
            })
        }
    except Exception as e:
        error_message = f"Error starting Fargate task: {str(e)}"
        logger.error(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }
