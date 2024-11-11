import unittest
import json
import os
from unittest.mock import patch, MagicMock
from lambda_trigger.trigger_aws_lambda import lambda_handler

class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        os.environ['CLUSTER_NAME'] = 'test-cluster'
        os.environ['TASK_DEFINITION'] = 'test-task'
        os.environ['SUBNET_ID'] = 'subnet-12345'
        os.environ['SECURITY_GROUP_ID'] = 'sg-12345'
        
        self.event = {
            'body': json.dumps({
                'provider': 'zoom',
                'meeting_id': '123-456-789',
                'meeting_link': 'https://zoom.us/j/123456789'
            })
        }

    def tearDown(self):
        for var in ['CLUSTER_NAME', 'TASK_DEFINITION', 'SUBNET_ID', 'SECURITY_GROUP_ID']:
            if var in os.environ:
                del os.environ[var]

    @patch('lambda_trigger.trigger_aws_lambda.boto3.client')
    def test_missing_environment_variables(self, mock_boto_client):
        del os.environ['SUBNET_ID']
        
        response = lambda_handler(self.event, None)
        
        self.assertEqual(response['statusCode'], 500)
        self.assertIn("Missing environment variables", response['body'])

    @patch('lambda_trigger.trigger_aws_lambda.boto3.client')
    def test_invalid_json_body(self, mock_boto_client):
        event = {'body': 'Invalid JSON'}
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Invalid or missing parameters", response['body'])

    @patch('lambda_trigger.trigger_aws_lambda.boto3.client')
    def test_missing_parameters_in_json_body(self, mock_boto_client):
        event = {
            'body': json.dumps({
                'provider': 'zoom',
                'meeting_id': '123-456-789'
            })
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Invalid or missing parameters", response['body'])

    @patch('lambda_trigger.trigger_aws_lambda.boto3.client')
    def test_successful_fargate_task_start(self, mock_boto_client):
        mock_ecs_client = MagicMock()
        mock_ecs_client.run_task.return_value = {
            'tasks': [{'taskArn': 'arn:aws:ecs:region:account-id:task/test-cluster/task-id'}]
        }
        mock_boto_client.return_value = mock_ecs_client
        
        response = lambda_handler(self.event, None)

        self.assertEqual(mock_boto_client.return_value, mock_ecs_client)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("Fargate task started successfully", response['body'])
        self.assertIn("taskArn", json.loads(response['body']))

    @patch('lambda_trigger.trigger_aws_lambda.boto3.client')
    def test_fargate_task_start_failure(self, mock_boto_client):
        mock_ecs_client = MagicMock()
        mock_ecs_client.run_task.side_effect = Exception("Fargate task failed to start")
        mock_boto_client.return_value = mock_ecs_client

        response = lambda_handler(self.event, None)
        
        self.assertEqual(response['statusCode'], 500)
        self.assertIn("Error starting Fargate task", response['body'])

    @patch('lambda_trigger.trigger_aws_lambda.boto3.client')
    def test_logging_information(self, mock_boto_client):
        with self.assertLogs('', level='INFO') as log:
            mock_ecs_client = MagicMock()
            mock_ecs_client.run_task.return_value = {
                'tasks': [{'taskArn': 'arn:aws:ecs:region:account-id:task/test-cluster/task-id'}]
            }
            mock_boto_client.return_value = mock_ecs_client

            lambda_handler(self.event, None)

            self.assertTrue(any("Execution ID" in message for message in log.output))
            self.assertTrue(any("Starting Fargate task..." in message for message in log.output))
            self.assertTrue(any("Fargate task started successfully" in message for message in log.output))

if __name__ == '__main__':
    unittest.main()
