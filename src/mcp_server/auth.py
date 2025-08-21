import os
import json
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
    Desktop OAuth (InstalledAppFlow) 기반 자격 증명 확보.
    - token_path가 있으면 불러오고, 필요시 refresh
    - 없거나 만료되었고 refresh 불가하면 브라우저 승인 플로우 실행
    """
    Path(token_path).parent.mkdir(parents=True, exist_ok=True)

    creds: Optional[Credentials] = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes=scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
            # 브라우저 자동 오픈
            creds = flow.run_local_server(port=0)
        # 저장
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds
