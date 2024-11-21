import unittest
from unittest.mock import patch, MagicMock
from app_bot.app_bot import app, GoogleMeetRecorder, TeamsRecorder, ZoomRecorder, boto3_client
from flask import json


class TestAppBot(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    @patch("app_bot.GoogleMeetRecorder.record_meeting")
    @patch("app_bot.GoogleMeetRecorder.save_timeline_to_s3")
    def test_record_google_meet(self, mock_save_timeline, mock_record_meeting):
        mock_record_meeting.return_value = None
        mock_save_timeline.return_value = None

        response = self.client.post(
            "/record",
            json={
                "name": "google_meet",
                "meeting_id": "test-meeting-id",
                "host_access_token": "test-google-token"
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_record_meeting.assert_called_once()
        mock_save_timeline.assert_called_once_with("google_meet")

    @patch("app_bot.TeamsRecorder.record_meeting")
    @patch("app_bot.TeamsRecorder.save_timeline_to_s3")
    def test_record_teams(self, mock_save_timeline, mock_record_meeting):
        mock_record_meeting.return_value = None
        mock_save_timeline.return_value = None

        response = self.client.post(
            "/record",
            json={
                "name": "teams",
                "meeting_id": "test-meeting-id",
                "host_access_token": "test-teams-token"
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_record_meeting.assert_called_once()
        mock_save_timeline.assert_called_once_with("teams")

    @patch("app_bot.ZoomRecorder.record_meeting")
    @patch("app_bot.ZoomRecorder.save_timeline_to_s3")
    def test_record_zoom(self, mock_save_timeline, mock_record_meeting):
        mock_record_meeting.return_value = None
        mock_save_timeline.return_value = None

        response = self.client.post(
            "/record",
            json={
                "name": "zoom",
                "meeting_id": "test-meeting-id",
                "host_access_token": "test-zoom-token"
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_record_meeting.assert_called_once()
        mock_save_timeline.assert_called_once_with("zoom")

    def test_invalid_platform(self):
        response = self.client.post(
            "/record",
            json={
                "name": "unsupported_platform",
                "meeting_id": "test-meeting-id",
                "host_access_token": "test-token"
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Unsupported platform", response.data)

    def test_missing_fields(self):
        response = self.client.post(
            "/record",
            json={
                "name": "zoom",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid request: Missing required fields", response.data)

    @patch("app_bot.boto3_client.put_object")
    def test_save_timeline_to_s3_success(self, mock_put_object):
        recorder = GoogleMeetRecorder("test-meeting-id", "test-google-token")
        mock_put_object.return_value = None
        recorder.save_timeline_to_s3("google_meet")
        mock_put_object.assert_called_once()

    @patch("app_bot.boto3_client.put_object")
    def test_save_timeline_to_s3_failure(self, mock_put_object):
        recorder = GoogleMeetRecorder("test-meeting-id", "test-google-token")
        mock_put_object.side_effect = Exception("S3 upload error")
        with self.assertRaises(Exception):
            recorder.save_timeline_to_s3("google_meet")

    @patch("app_bot.GoogleMeetRecorder.record_meeting")
    def test_google_meet_record_meeting(self, mock_record_meeting):
        recorder = GoogleMeetRecorder("test-meeting-id", "test-google-token")
        mock_record_meeting.return_value = None
        recorder.record_meeting()
        mock_record_meeting.assert_called_once()

    @patch("app_bot.TeamsRecorder.record_meeting")
    def test_teams_record_meeting(self, mock_record_meeting):
        recorder = TeamsRecorder("test-meeting-id", "test-teams-token")
        mock_record_meeting.return_value = None
        recorder.record_meeting()
        mock_record_meeting.assert_called_once()

    @patch("app_bot.ZoomRecorder.record_meeting")
    def test_zoom_record_meeting(self, mock_record_meeting):
        recorder = ZoomRecorder("test-meeting-id", "test-zoom-token")
        mock_record_meeting.return_value = None
        recorder.record_meeting()
        mock_record_meeting.assert_called_once()


if __name__ == "__main__":
    unittest.main()
