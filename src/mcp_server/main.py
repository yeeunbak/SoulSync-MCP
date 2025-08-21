from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
import uuid

from .models import (
    MoodLogArgs, MoodLogResult,
    JournalAddArgs, JournalAddResult,
    ContentGetArgs, ContentGetResult,
    CrisisArgs, CrisisResult,
    # NEW
    CalendarBookArgs, CalendarBookResult,
    EmailComposeDraftArgs, EmailComposeDraftResult
)
from .store import save_mood_log, save_journal
from .resources import load_modules, load_crisis_numbers

app = FastAPI(title="SoulSync MCP Server")

MODULES = load_modules()
CRISIS = load_crisis_numbers()

def schema_of(model):
    return model.model_json_schema()

CAPABILITIES = {
    "mood.log": {
        "args_schema": schema_of(MoodLogArgs),
        "result_schema": schema_of(MoodLogResult),
        "description": "기분/수면/불안 지표를 기록합니다."
    },
    "journal.add": {
        "args_schema": schema_of(JournalAddArgs),
        "result_schema": schema_of(JournalAddResult),
        "description": "저널 항목을 저장합니다(민감정보는 수집 금지 권장)."
    },
    "content.module.get": {
        "args_schema": schema_of(ContentGetArgs),
        "result_schema": schema_of(ContentGetResult),
        "description": "주제별 셀프케어 모듈(단계별 가이드)을 제공합니다."
    },
    "crisis.get_numbers": {
        "args_schema": schema_of(CrisisArgs),
        "result_schema": schema_of(CrisisResult),
        "description": "지역 위기 연락처를 반환합니다."
    },
    # NEW
    "calendar.book_slot": {
        "args_schema": schema_of(CalendarBookArgs),
        "result_schema": schema_of(CalendarBookResult),
        "description": "상담 예약 초안(확인 필요)을 만듭니다."
    },
    "email.compose_draft": {
        "args_schema": schema_of(EmailComposeDraftArgs),
        "result_schema": schema_of(EmailComposeDraftResult),
        "description": "이메일 초안을 생성합니다(자동 발송 없음)."
    }
}

@app.get("/capabilities")
def list_capabilities():
    return CAPABILITIES

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.post("/invoke/mood.log", response_model=MoodLogResult)
def invoke_mood_log(args: MoodLogArgs):
    log_id = save_mood_log(args.user_id, args.model_dump())
    return MoodLogResult(log_id=log_id)

@app.post("/invoke/journal.add", response_model=JournalAddResult)
def invoke_journal_add(args: JournalAddArgs):
    entry_id = save_journal(args.user_id, args.text, args.tags or [])
    return JournalAddResult(entry_id=entry_id)

@app.post("/invoke/content.module.get", response_model=ContentGetResult)
def invoke_content_get(args: ContentGetArgs):
    topic = args.topic
    mod = MODULES.get(topic) or MODULES["anxiety-first-aid"]
    return ContentGetResult(
        id=mod["id"], title=mod["title"], steps=mod["steps"], cautions=mod["cautions"]
    )

@app.post("/invoke/crisis.get_numbers", response_model=CrisisResult)
def invoke_crisis(args: CrisisArgs):
    return CrisisResult(**CRISIS)

# ===== NEW: 외부 액션 데모 엔드포인트 =====
@app.post("/invoke/calendar.book_slot", response_model=CalendarBookResult)
def invoke_calendar_book(args: CalendarBookArgs):
    # 실제로는 외부 캘린더 API 호출 & 초안 상태로 저장
    return CalendarBookResult(
        booking_id=str(uuid.uuid4()),
        status="draft",
        datetime=args.datetime,
        provider_id=args.provider_id,
        reason=args.reason
    )

@app.post("/invoke/email.compose_draft", response_model=EmailComposeDraftResult)
def invoke_email_compose(args: EmailComposeDraftArgs):
    # 실제 발송 없음. 미리보기만 반환
    return EmailComposeDraftResult(
        draft_id=str(uuid.uuid4()),
        preview_subject=args.subject,
        preview_body=args.body
    )
