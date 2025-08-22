# MCP 표준 서버 (FastMCP) — 기존 내부 로직을 그대로 래핑
from mcp.server.fastmcp import FastMCP
from typing import Optional
# 우리 내부 함수/자원 재사용
from src.mcp_server.store import save_mood_log, save_journal
from src.mcp_server.resources import load_modules, load_crisis_numbers

from src.mcp_server.gcal_client import create_event
from src.mcp_server.gmail_client import create_draft, send_message, send_draft
from dateutil import parser as dtparser

mcp = FastMCP("SoulSync-MCP")

MODULES = load_modules()
CRISIS = load_crisis_numbers()

@mcp.tool()
def mood_log(user_id: str, valence: int, sleep_hours: Optional[float]=None, anxiety0_10: Optional[int]=None) -> dict:
    """기분/수면/불안 지표 기록"""
    log_id = save_mood_log(user_id, {"valence":valence, "sleep_hours":sleep_hours, "anxiety0_10":anxiety0_10})
    return {"log_id": log_id}

@mcp.tool()
def journal_add(user_id: str, text: str, tags: list[str] | None = None) -> dict:
    """저널 항목 저장(민감정보는 피하세요)"""
    entry_id = save_journal(user_id, text, tags or [])
    return {"entry_id": entry_id}

@mcp.tool()
def content_module_get(topic: str, level: str = "beginner", locale: str = "ko-KR") -> dict:
    """주제별 셀프케어 모듈 반환"""
    mod = MODULES.get(topic) or MODULES["anxiety-first-aid"]
    return {"id": mod["id"], "title": mod["title"], "steps": mod["steps"], "cautions": mod["cautions"]}

@mcp.tool()
def crisis_get_numbers(locale: str = "ko-KR") -> dict:
    """지역 위기 연락처 반환(출시 전 최신화 필요)"""
    return CRISIS

# (선택) 나중에 구글 캘린더/지메일 래핑 도구도 여기로 추가 가능
# @mcp.tool()
# def calendar_create_event(datetime_iso: str, reason: str | None = None) -> dict: ...
# @mcp.tool()
# def gmail_compose_draft(to: str, subject: str, body: str) -> dict: ...
@mcp.tool()
def calendar_create_event(datetime_iso: str,
                          duration_min: int = 60,
                          reason: Optional[str] = None,
                          timezone: str = "Asia/Seoul") -> dict:
    """Google Calendar에 개인 이벤트 생성(알림·초대 없음)"""
    return create_event(
        start_iso=datetime_iso,
        duration_min=duration_min,
        summary="[확인됨] 상담 예약",
        description=reason or "SoulSync에서 생성",
        timezone=timezone
    )

@mcp.tool()
def calendar_create_event_nl(datetime_text: str,
                             duration_min: int = 60,
                             reason: Optional[str] = None,
                             timezone: str = "Asia/Seoul") -> dict:
    """자연어 시간(예: '다음 주 수요일 3시')을 받아 이벤트 생성"""
    dt = dtparser.parse(datetime_text, fuzzy=True)
    if not dt:
        raise ValueError("시간을 해석할 수 없습니다.")
    return calendar_create_event(dt.isoformat(), duration_min, reason, timezone)

@mcp.tool()
def gmail_compose_draft(to: str, subject: str, body: str) -> dict:
    """Gmail에 이메일 초안 생성(보내지 않음)"""
    return create_draft(to, subject, body)

@mcp.tool()
def gmail_send(to: str, subject: str, body: str, to_name: str | None = None) -> dict:
    """
    Gmail로 이메일을 즉시 전송합니다.
    - to: 수신자 이메일 (예: user@example.com)
    - to_name: 수신자 표시 이름(옵션, 예: '홍길동')
    """
    return send_message(to=to, subject=subject, body=body, to_name=to_name)

@mcp.tool()
def gmail_send_draft(draft_id: str) -> dict:
    """
    compose_draft로 만든 초안을 전송합니다.
    - draft_id: 초안 ID
    """
    return send_draft(draft_id)