import requests, os
from typing import Dict, Any, Optional
from .intents import RULES
from .policies import Policy

MCP_BASE = os.environ.get("MCP_BASE", "http://localhost:8081")

def _match(text: str):
    for rule in RULES:
        m = rule.pattern.search(text)
        if m:
            return rule, m
    return None, None

def _invoke(tool: str, args: Dict[str, Any]):
    resp = requests.post(f"{MCP_BASE}/invoke/{tool}", json=args, timeout=15)
    resp.raise_for_status()
    return resp.json()

# NEW: CLI에서 확인 후 실제 호출할 때 쓰기 위해 공개 함수로 노출
def invoke(tool: str, args: Dict[str, Any]):
    return _invoke(tool, args)

def route(user_id: str, text: str) -> Dict[str, Any]:
    rule, m = _match(text)
    if not rule:
        return {"type":"message","content":"의도를 이해하지 못했어요. 예: “기분 -1 / 불안 7 기록”, “저널에 '...' 저장”, “호흡 가이드 시작”, “상담 예약 잡아줘”, “상담사에게 이메일 초안”"}

    args = rule.slot_extractor(m)
    payload = {"user_id": user_id, **args} if rule.to_tool in ("mood.log","journal.add","calendar.book_slot") else args

    if rule.policy == Policy.AUTO:
        result = _invoke(rule.to_tool, payload)
        return {"type":"auto_done","tool":rule.to_tool,"args":payload,"result":result}

    if rule.policy == Policy.CONFIRM:
        return {"type":"confirm_required","tool":rule.to_tool,"args":payload}

    if rule.policy == Policy.DRAFT:
        draft = _invoke(rule.to_tool, payload)
        return {"type":"draft","tool":rule.toool if hasattr(rule,'toool') else rule.to_tool,"draft":draft}

    return {"type":"message","content":"정책을 처리하지 못했어요."}
