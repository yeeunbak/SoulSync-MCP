# MCP 표준 서버 (FastMCP) — 기존 내부 로직을 그대로 래핑
from mcp.server.fastmcp import FastMCP
from typing import Optional
# 우리 내부 함수/자원 재사용
from src.mcp_server.store import save_mood_log, save_journal
from src.mcp_server.resources import load_modules, load_crisis_numbers

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
