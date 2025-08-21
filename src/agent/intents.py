import re
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Any
from .policies import Policy
import dateparser

@dataclass
class IntentRule:
    name: str
    pattern: re.Pattern
    to_tool: str
    policy: Policy
    slot_extractor: Callable[[re.Match], Dict[str, Any]]

# -------- 슬롯 추출기 --------
def _slots_log_mood(m: re.Match) -> Dict[str, Any]:
    valence = int(m.group("val"))
    anxiety = m.group("anx")
    return {"valence": valence, "anxiety0_10": int(anxiety) if anxiety else None}

def _slots_add_journal(m: re.Match) -> Dict[str, Any]:
    return {"text": m.group("text")}

def _slots_breathing(m: re.Match) -> Dict[str, Any]:
    return {"topic": "breathing", "level": "beginner"}

def _slots_crisis(m: re.Match) -> Dict[str, Any]:
    return {}

# NEW: 자연어 날짜 파싱 → ISO8601
def _parse_datetime_ko(text: str) -> Optional[str]:
    dt = dateparser.parse(
        text, languages=["ko"], settings={"PREFER_DATES_FROM": "future"}
    )
    return dt.isoformat() if dt else None

# NEW: 상담 예약
def _slots_book_calendar(m: re.Match) -> Dict[str, Any]:
    iso = _parse_datetime_ko(m.string)
    return {"datetime": iso or "1970-01-01T09:00:00", "reason": "상담 예약"}

# NEW: 이메일 초안
def _slots_email_draft(m: re.Match) -> Dict[str, Any]:
    to = m.group("to") or "상담사"
    subject = "SoulSync 진행 요약"
    body = "안녕하세요, 최근 진행 상황과 다음 계획을 공유드립니다."
    return {"to": to, "subject": subject, "body": body}

# -------- 규칙 --------
RULES = [
    # 내부 자동 액션
    IntentRule(
        name="log_mood",
        pattern=re.compile(r"(?:기분\s*(?P<val>-?2|-?1|0|\+?1|\+?2))(?:(?:\s*[/,]\s*불안\s*(?P<anx>\d{1,2}))?)\s*(?:기록|저장)", re.I),
        to_tool="mood.log",
        policy=Policy.AUTO,
        slot_extractor=_slots_log_mood
    ),
    IntentRule(
        name="add_journal",
        pattern=re.compile(r"(?:저널|일지|기록)\s*(?:에)?\s*['\"](?P<text>.+?)['\"]\s*(?:저장|추가)", re.I),
        to_tool="journal.add",
        policy=Policy.AUTO,
        slot_extractor=_slots_add_journal
    ),
    IntentRule(
        name="start_breathing",
        pattern=re.compile(r"(?:호흡|호흡법|숨쉬기)\s*(?:시작|가이드)", re.I),
        to_tool="content.module.get",
        policy=Policy.AUTO,
        slot_extractor=_slots_breathing
    ),
    IntentRule(
        name="crisis_numbers",
        pattern=re.compile(r"(?:무서워|도와줘|위기|너무힘들어|어떻게해야해)", re.I),
        to_tool="crisis.get_numbers",
        policy=Policy.AUTO,
        slot_extractor=_slots_crisis
    ),

    # ===== NEW: 외부 액션 =====
    # 상담 예약(확인 필요)
    IntentRule(
        name="book_session",
        pattern=re.compile(r"(?:상담|상담센터|상담소).*(?:예약|잡아줘|일정)", re.I),
        to_tool="calendar.book_slot",
        policy=Policy.CONFIRM,
        slot_extractor=_slots_book_calendar
    ),
    # 이메일 초안
    IntentRule(
        name="email_draft",
        pattern=re.compile(r"(?:(?:메일|이메일).*(?:초안|작성))|(?:(?P<to>.+?)에게\s*(?:메일|이메일).*(?:초안|작성))", re.I),
        to_tool="email.compose_draft",
        policy=Policy.DRAFT,
        slot_extractor=_slots_email_draft
    ),
]
