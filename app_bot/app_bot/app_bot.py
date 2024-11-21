from flask import Flask, request, jsonify
import boto3
import logging
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials as GoogleCredentials
from googleapiclient.discovery import build
from msal import ConfidentialClientApplication
import requests
import json

app = Flask(__name__)

BUCKET_NAME = "name-of-the-bucket-s3"
boto3_client = boto3.client("s3")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GOOGLE_CREDENTIALS = {
    "token": "your-google-token",
    "refresh_token": "your-google-refresh-token",
    "client_id": "your-google-client-id",
    "client_secret": "your-google-client-secret",
    "token_uri": "https://oauth2.googleapis.com/token"
}

AZURE_CREDENTIALS = {
    "client_id": "your-azure-client-id",
    "client_secret": "your-azure-client-secret",
    "tenant_id": "your-azure-tenant-id"
}

ZOOM_CREDENTIALS = {
    "client_id": "your-zoom-client-id",
    "client_secret": "your-zoom-client-secret"
}

class MeetingRecorder:
    def __init__(self, meeting_id, host_access_token):
        self.meeting_id = meeting_id
        self.host_access_token = host_access_token
        self.timeline = []

    def log_event(self, event):
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = {"timestamp": timestamp, "event": event}
        self.timeline.append(log_entry)
        logger.info(f"Logged event: {log_entry}")

    def save_timeline_to_s3(self, platform):
        try:
            filename = f"{self.meeting_id}_{platform}_timeline.json"
            boto3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=filename,
                Body=json.dumps(self.timeline)
            )
            logger.info(f"Timeline saved to S3: {filename}")
        except Exception as e:
            logger.error(f"Failed to save timeline to S3: {e}")
            raise

class GoogleMeetRecorder(MeetingRecorder):
    def record_meeting(self):
        self.log_event("Google Meet recording started")
        creds = GoogleCredentials(**GOOGLE_CREDENTIALS)
        service = build("calendar", "v3", credentials=creds)
        events_result = service.events().list(calendarId="primary").execute()
        events = events_result.get("items", [])
        if events:
            self.log_event("Meeting event found in Google Calendar")
        else:
            self.log_event("No recordings found for this meeting.")

class TeamsRecorder(MeetingRecorder):
    def record_meeting(self):
        self.log_event("Teams meeting recording started")
        app = ConfidentialClientApplication(
            AZURE_CREDENTIALS["client_id"],
            authority=f"https://login.microsoftonline.com/{AZURE_CREDENTIALS['tenant_id']}",
            client_credential=AZURE_CREDENTIALS["client_secret"]
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in result:
            headers = {"Authorization": f"Bearer {result['access_token']}"}
            response = requests.get(
                f"https://graph.microsoft.com/v1.0/me/events/{self.meeting_id}",
                headers=headers
            )
            if response.status_code == 200:
                self.log_event("Meeting details retrieved successfully")
            else:
                self.log_event(f"Failed to retrieve meeting details: {response.status_code}")
        else:
            self.log_event("Authentication failed for Microsoft Graph")

class ZoomRecorder(MeetingRecorder):
    def record_meeting(self):
        self.log_event("Zoom meeting recording started")
        url = f"https://api.zoom.us/v2/meetings/{self.meeting_id}/recordings"
        headers = {
            "Authorization": f"Bearer {self.host_access_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.log_event("Zoom meeting details fetched successfully")
        else:
            self.log_event(
                f"Failed to fetch meeting details. Status Code: {response.status_code}, Response: {response.text}"
            )

@app.route("/record", methods=["POST"])
def record_meeting():
    try:
        logger.info("Received a request to record a meeting")
        body = request.get_json()
        logger.info(f"Request body: {body}")

        platform = body.get("name")
        meeting_id = body.get("meeting_id")
        host_access_token = body.get("host_access_token")
        if not all([platform, meeting_id, host_access_token]):
            logger.warning("Invalid request: Missing required fields")
            return jsonify({"message": "Invalid request: Missing required fields"}), 400

        recorder = None
        if platform == "google_meet":
            recorder = GoogleMeetRecorder(meeting_id, host_access_token)
        elif platform == "teams":
            recorder = TeamsRecorder(meeting_id, host_access_token)
        elif platform == "zoom":
            recorder = ZoomRecorder(meeting_id, host_access_token)
        else:
            logger.warning(f"Unsupported platform: {platform}")
            return jsonify({"message": "Unsupported platform"}), 400

        recorder.record_meeting()
        recorder.save_timeline_to_s3(platform)

        logger.info("Recording completed successfully")
        return jsonify({"message": "Recording completed successfully"}), 200

    except Exception as e:
        logger.error(f"Unhandled exception in record_meeting: {e}")
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
