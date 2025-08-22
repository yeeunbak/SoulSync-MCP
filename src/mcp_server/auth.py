# src/mcp_server/auth.py
import os
from pathlib import Path
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def ensure_credentials(
    client_secret_path: str,
    token_path: str,
    scopes: List[str],
) -> Credentials:
    """
    InstalledAppFlow 기반 OAuth 자격 확보.
    - 토큰이 없거나, 만료되었거나, **요구 스코프가 부족하면** 재인증(브라우저 동의).
    """
    Path(token_path).parent.mkdir(parents=True, exist_ok=True)

    creds: Optional[Credentials] = None
    if os.path.exists(token_path):
        try:
            # 저장된 토큰을 우선 불러옴
            creds = Credentials.from_authorized_user_file(token_path, scopes=scopes)
        except Exception:
            creds = None  # 손상/구버전 형식 등

    # 필요 시 새로고침 시도
    if creds and getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
        try:
            creds.refresh(Request())
        except Exception:
            creds = None  # 새로 동의 받도록

    # === 핵심: 스코프 부족/무효하면 재동의 ===
    def _has_all_scopes(c: Credentials) -> bool:
        try:
            granted = set(getattr(c, "scopes", []) or [])
            return set(scopes).issubset(granted)
        except Exception:
            return False

    if (creds is None) or (not creds.valid) or (not _has_all_scopes(creds)):
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
        # 로컬 포트 자동 선택, 브라우저 오픈
        creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds
