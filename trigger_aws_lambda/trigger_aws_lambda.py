import json
import boto3
import os
import logging
import uuid
from datetime import datetime

ecs_client = boto3.client('ecs')
s3_client = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    log_bucket_name = os.environ.get('LOG_BUCKET_NAME')
    cluster_name = os.environ['CLUSTER_NAME']
    task_definition = os.environ['TASK_DEFINITION']
    subnet_id = os.environ['SUBNET_ID']
    security_group_id = os.environ['SECURITY_GROUP_ID']

    execution_id = str(uuid.uuid4())
    log_file_name = f"lambda_logs/{execution_id}.log"
    log_content = []

    log_content.append(f"Execution ID: {execution_id}")
    log_content.append(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        body = json.loads(event['body'])
        provider = body['provider']
        meeting_id = body['meeting_id']
        meeting_link = body['meeting_link']
        
        log_content.append(f"Provider: {provider}")
        log_content.append(f"Meeting ID: {meeting_id}")
        log_content.append(f"Meeting Link: {meeting_link}")
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        error_message = f"Invalid or missing parameters: {str(e)}"
        log_content.append(error_message)
        upload_log_to_s3(log_bucket_name, log_file_name, "\n".join(log_content))
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_message})
        }

    environment_variables = [
        {'name': 'PROVIDER', 'value': provider},
        {'name': 'MEETING_ID', 'value': meeting_id},
        {'name': 'MEETING_LINK', 'value': meeting_link}
    ]

    try:
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
        log_content.append(f"Fargate task started successfully. Task ARN: {task_arn}")
        
        upload_log_to_s3(log_bucket_name, log_file_name, "\n".join(log_content))
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Fargate task started successfully.",
                "taskArn": task_arn
            })
        }
    except Exception as e:
        error_message = f"Error starting Fargate task: {str(e)}"
        log_content.append(error_message)
        
        upload_log_to_s3(log_bucket_name, log_file_name, "\n".join(log_content))
        
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }

def upload_log_to_s3(bucket_name, file_name, log_content):
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=log_content
        )
        logger.info(f"Log file successfully uploaded to S3: s3://{bucket_name}/{file_name}")
    except Exception as e:
        logger.error(f"Failed to upload log to S3: {str(e)}")
