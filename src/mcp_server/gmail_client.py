import base64
from email.mime.text import MIMEText
from typing import Dict, Any

from googleapiclient.discovery import build

from .config import GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, GMAIL_SCOPES
from .auth import ensure_credentials


def _create_mime_text(to: str, subject: str, body: str) -> MIMEText:
    msg = MIMEText(body, _charset="utf-8")
    msg["to"] = to
    msg["subject"] = subject
    return msg


def compose_draft(to: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Gmail 초안 생성 (보내지 않고 draft에 저장)
    """
    creds = ensure_credentials(GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, GMAIL_SCOPES)
    service = build("gmail", "v1", credentials=creds)

    msg = _create_mime_text(to, subject, body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    draft = service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return {"id": draft.get("id"), "messageId": draft.get("message", {}).get("id")}
