import json, os
from typing import Dict, Any

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(BASE, "src", "data")

def load_modules() -> Dict[str, Any]:
    path = os.path.join(DATA, "modules_ko.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_crisis_numbers() -> Dict[str, Any]:
    path = os.path.join(DATA, "crisis_numbers_ko.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
