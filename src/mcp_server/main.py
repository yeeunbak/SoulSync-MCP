from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import MCP_HOST, MCP_PORT
from .gcal_client import create_event_nl
from .gmail_client import compose_draft

app = FastAPI(title="SoulSync MCP Server")

# ---- Models ----
class CalendarCreateEventNL(BaseModel):
    datetime_text: str
    duration_min: int
    reason: str
    timezone: str | None = "Asia/Seoul"
    description: str | None = None

class GmailComposeDraft(BaseModel):
    to: str
    subject: str
    body: str


# ---- Capabilities ----
@app.get("/capabilities")
def capabilities() -> Dict[str, Any]:
    """
    MCP가 노출하는 툴/엔드포인트의 ID를 알려줌
    """
    return {
        "tools": [
            {
                "id": "calendar.create_event_nl",
                "input": {
                    "datetime_text": "string",
                    "duration_min": "number",
                    "reason": "string",
                    "timezone": "string (optional)",
                    "description": "string (optional)",
                },
                "output": {"id": "string", "htmlLink": "string", "status": "string"},
            },
            {
                "id": "gmail.compose_draft",
                "input": {"to": "string", "subject": "string", "body": "string"},
                "output": {"id": "string", "messageId": "string"},
            },
        ]
    }


# ---- Invoke endpoints ----
@app.post("/invoke/calendar.create_event_nl")
def invoke_calendar_create_event_nl(payload: CalendarCreateEventNL):
    try:
        res = create_event_nl(
            datetime_text=payload.datetime_text,
            duration_min=payload.duration_min,
            summary=payload.reason,
            timezone=payload.timezone or "Asia/Seoul",
            description=payload.description,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calendar error: {e}")


@app.post("/invoke/gmail.compose_draft")
def invoke_gmail_compose_draft(payload: GmailComposeDraft):
    try:
        res = compose_draft(
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gmail error: {e}")


# 개발용 실행 힌트:
# uvicorn src.mcp_server.main:app --host 127.0.0.1 --port 8088
