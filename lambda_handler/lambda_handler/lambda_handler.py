import json
import logging
import os
import boto3
import time
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AUTO_SCALING_URL = os.environ.get("AUTO_SCALING_URL")

session = boto3.session.Session()
client = session.client('apigateway')

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 1

def lambda_handler(event, context):
    try:
        if event.get("httpMethod") != "POST":
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method not allowed. Only POST requests are accepted."})
            }

        try:
            body = json.loads(event.get("body", "{}"))
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON format in the request body"})
            }

        required_fields = ["name", "meeting_id", "host_access_token"]
        if not all(field in body for field in required_fields):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields in the JSON body"})
            }

        logger.info("Received JSON: %s", json.dumps(body))

        for attempt in range(1, MAX_RETRIES + 2):
            try:
                logger.info(f"Attempt {attempt} to send request to Auto Scaling Group")

                response = client.invoke(
                    FunctionName=AUTO_SCALING_URL,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(body)
                )

                response_payload = json.loads(response['Payload'].read().decode("utf-8"))

                if response["StatusCode"] == 200:
                    logger.info("Request sent successfully to Auto Scaling Group.")
                    return {
                        "statusCode": 200,
                        "body": json.dumps({"message": "Request sent successfully", "response": response_payload})
                    }
                else:
                    logger.warning("Request failed with status code: %s", response["StatusCode"])
                    raise Exception("Non-200 status code received")

            except (BotoCoreError, ClientError, Exception) as e:
                logger.error("Error in attempt %d: %s", attempt, str(e))
                
                if attempt < MAX_RETRIES + 1:
                    logger.info(f"Retrying in {RETRY_DELAY_SECONDS} second(s)...")
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    logger.error("All attempts to send request failed.")
                    return {
                        "statusCode": 502,
                        "body": json.dumps({"error": "Failed to send request to Auto Scaling Group after retries"})
                    }

    except Exception as e:
        logger.error("Unhandled error occurred: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }
