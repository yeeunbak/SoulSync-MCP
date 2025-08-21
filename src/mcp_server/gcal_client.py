# src/mcp_server/gcal_client.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Sequence

from dateutil import parser as du_parser
from googleapiclient.discovery import build

from .config import GCAL_CREDENTIALS_PATH, GCAL_TOKEN_PATH, GCAL_SCOPES
from .auth import ensure_credentials


def _parse_datetime(datetime_text: str) -> datetime:
    """
    문자열(자연어 일부 포함)을 datetime으로 파싱합니다.
    - 예: "2025-08-25 15:00", "2025-08-25T15:00", "Aug 25 2025 3pm"
    - 한국어 상대표현은 제한될 수 있으므로 가급적 ISO 형식을 권장합니다.
    실패 시 ValueError가 발생합니다.
    """
    return du_parser.parse(datetime_text, fuzzy=True)


def create_event_nl(
    datetime_text: str,
    duration_min: int,
    summary: str,
    *,
    timezone: str = "Asia/Seoul",
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    자연어/문자열 시간 + 지속시간(분)으로 Google Calendar 이벤트 생성.

    Parameters
    ----------
    datetime_text : str
        시작 시각을 나타내는 문자열. (예: "2025-08-27 15:00")
    duration_min : int
        이벤트 지속 시간(분).
    summary : str
        이벤트 제목.
    timezone : str, optional
        IANA 타임존 문자열(기본 "Asia/Seoul").
    description : str, optional
        이벤트 설명.
    location : str, optional
        이벤트 위치.
    attendees : Sequence[str], optional
        참석자 이메일 리스트. 예: ["a@example.com", "b@example.com"]

    Returns
    -------
    Dict[str, Any]
        생성된 이벤트의 요약 정보(id, htmlLink, status, start, end).
    """
    if duration_min <= 0:
        raise ValueError("duration_min must be a positive integer.")

    # OAuth 자격 증명 확보 (없으면 브라우저 승인 플로우 실행)
    creds = ensure_credentials(GCAL_CREDENTIALS_PATH, GCAL_TOKEN_PATH, GCAL_SCOPES)
    service = build("calendar", "v3", credentials=creds)

    start_dt = _parse_datetime(datetime_text)
    end_dt = start_dt + timedelta(minutes=duration_min)

    event_body: Dict[str, Any] = {
        "summary": summary,
        "description": description or "",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone},
    }

    if location:
        event_body["location"] = location
    if attendees:
        event_body["attendees"] = [{"email": email} for email in attendees]

    created = service.events().insert(calendarId="primary", body=event_body).execute()

    return {
        "id": created.get("id"),
        "htmlLink": created.get("htmlLink"),
        "status": created.get("status"),
        "start": created.get("start"),
        "end": created.get("end"),
    }
