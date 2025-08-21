import json, os, uuid, datetime
from typing import Dict, Any

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STORAGE = os.path.join(BASE, "storage")
os.makedirs(STORAGE, exist_ok=True)

def _append_jsonl(path: str, obj: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def save_mood_log(user_id: str, payload: Dict[str, Any]) -> str:
    log_id = str(uuid.uuid4())
    rec = {
        "log_id": log_id,
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        **payload
    }
    _append_jsonl(os.path.join(STORAGE, "mood_logs.jsonl"), rec)
    return log_id

def save_journal(user_id: str, text: str, tags: list[str]) -> str:
    entry_id = str(uuid.uuid4())
    rec = {
        "entry_id": entry_id,
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "text": text,
        "tags": tags or []
    }
    _append_jsonl(os.path.join(STORAGE, "journal.jsonl"), rec)
    return entry_id
