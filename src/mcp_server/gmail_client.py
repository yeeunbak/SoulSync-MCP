import os, base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SECRETS = os.path.join(BASE, "secrets"); os.makedirs(SECRETS, exist_ok=True)
STORAGE = os.path.join(BASE, "storage"); os.makedirs(STORAGE, exist_ok=True)

CRED_PATH = os.path.join(SECRETS, "gmail_credentials.json")
TOKEN_PATH = os.path.join(STORAGE, "gmail_token.json")
# 초안만 만들기: compose 권한 (실발송은 나중에 send 스코프 추가)
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

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
                raise FileNotFoundError(f"OAuth credentials not found: {CRED_PATH}")
            flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds

def create_draft(to: str, subject: str, body: str) -> dict:
    creds = _get_creds()
    service = build("gmail", "v1", credentials=creds)
    msg = MIMEText(body, _charset="utf-8")
    msg["to"] = to; msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    created = service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()
    return {"id": created.get("id")}
