import os
from datetime import timedelta
from dateutil import parser as dtparser

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SECRETS = os.path.join(BASE, "secrets"); os.makedirs(SECRETS, exist_ok=True)
STORAGE = os.path.join(BASE, "storage"); os.makedirs(STORAGE, exist_ok=True)

CRED_PATH = os.path.join(SECRETS, "gcal_credentials.json")
TOKEN_PATH = os.path.join(STORAGE, "gcal_token.json")
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def _get_creds():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            if not os.path.exists(CRED_PATH):
                raise FileNotFoundError(f"Google OAuth credentials not found: {CRED_PATH}")
            flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds

def create_event(start_iso: str,
                 duration_min: int = 60,
                 summary: str = "[확인됨] SoulSync 상담 예약",
                 description: str = "SoulSync에서 생성된 예약입니다.",
                 calendar_id: str = "primary",
                 timezone: str = "Asia/Seoul") -> dict:
    creds = _get_creds()
    service = build("calendar", "v3", credentials=creds)

    start_dt = dtparser.isoparse(start_iso)       # "2025-09-03T15:00:00"
    end_dt = start_dt + timedelta(minutes=duration_min)

    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
        "end":   {"dateTime": end_dt.isoformat(),   "timeZone": timezone},
        "visibility": "private"
    }

    created = service.events().insert(
        calendarId=calendar_id, body=event, sendUpdates="none"
    ).execute()

    return {
        "id": created.get("id"),
        "htmlLink": created.get("htmlLink"),
        "summary": created.get("summary"),
        "start": created.get("start"),
        "end": created.get("end"),
    }
