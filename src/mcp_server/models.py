from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- mood.log ---
class MoodLogArgs(BaseModel):
    user_id: str
    valence: int = Field(..., ge=-2, le=2, description="-2(매우 나쁨) ~ +2(매우 좋음)")
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    anxiety0_10: Optional[int] = Field(None, ge=0, le=10)

class MoodLogResult(BaseModel):
    log_id: str

# --- journal.add ---
class JournalAddArgs(BaseModel):
    user_id: str
    text: str
    tags: Optional[List[str]] = []

class JournalAddResult(BaseModel):
    entry_id: str

# --- content.module.get ---
class ContentGetArgs(BaseModel):
    topic: str
    level: Optional[Literal["beginner","intermediate","advanced"]] = "beginner"
    locale: Optional[str] = "ko-KR"

class ContentGetResult(BaseModel):
    id: str
    title: str
    steps: List[str]
    cautions: List[str]

# --- crisis.get_numbers ---
class CrisisArgs(BaseModel):
    locale: Optional[str] = "ko-KR"

class CrisisResult(BaseModel):
    locale: str
    emergency: str
    police: str
    suicide: str
    mental_health: str
    welfare: str
    women: str
    note: Optional[str] = None

# ===== NEW: 외부 액션 데모 =====
# --- calendar.book_slot (확인 후 실행) ---
class CalendarBookArgs(BaseModel):
    user_id: str
    datetime: str                   # ISO8601 문자열로 전달
    provider_id: Optional[str] = None
    reason: Optional[str] = None

class CalendarBookResult(BaseModel):
    booking_id: str
    status: Literal["draft","confirmed"] = "draft"
    datetime: str
    provider_id: Optional[str] = None
    reason: Optional[str] = None

# --- email.compose_draft (초안만 생성) ---
class EmailComposeDraftArgs(BaseModel):
    to: str
    subject: str
    body: str

class EmailComposeDraftResult(BaseModel):
    draft_id: str
    preview_subject: str
    preview_body: str
