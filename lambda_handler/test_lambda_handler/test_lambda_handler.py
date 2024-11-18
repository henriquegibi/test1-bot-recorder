import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_handler.lambda_handler import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("lambda_handler.lambda_handler.client")
    def test_invalid_http_method(self, mock_client):
        event = {
            "httpMethod": "GET",
            "body": json.dumps({
                "name": "test",
                "meeting_id": "123",
                "host_access_token": "token"
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 405)
        self.assertIn("Method not allowed", response["body"])

    @patch("lambda_handler.lambda_handler.client")
    def test_invalid_json_body(self, mock_client):
        event = {
            "httpMethod": "POST",
            "body": "invalid_json"
        }
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Invalid JSON format", response["body"])

    @patch("lambda_handler.lambda_handler.client")
    def test_missing_required_fields(self, mock_client):
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "name": "test"
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Missing required fields", response["body"])

    @patch("lambda_handler.lambda_handler.client")
    def test_request_success(self, mock_client):
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "name": "test",
                "meeting_id": "123",
                "host_access_token": "token"
            })
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "success"}).encode("utf-8")
        mock_client.invoke.return_value = {
            "StatusCode": 200,
            "Payload": mock_response
        }

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Request sent successfully", response["body"])

    @patch("lambda_handler.lambda_handler.client")
    @patch("lambda_handler.lambda_handler.time.sleep", return_value=None)
    def test_request_failure_after_retries(self, mock_sleep, mock_client):
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "name": "test",
                "meeting_id": "123",
                "host_access_token": "token"
            })
        }
        mock_client.invoke.side_effect = Exception("Test exception")

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 502)
        self.assertIn("Failed to send request", response["body"])

if __name__ == "__main__":
    unittest.main()
