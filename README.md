# 로컬 실행 가이드 ( MCP : Google Calendar + Gmail )

### 요구사항
- Python 3.10+ (권장 3.11)
- Node.js LTS (npx 사용) → `node -v` `npm -v` 버전 확인



## 1) 가상환경설정

1) 레포 폴더로 이동
   
   `cd C:\SoulSync-MCP`

2) 가상환경 생성/활성화
   
   `python -m venv .venv`

   `.\.venv\Scripts\Activate.ps1`

3) 패키지 설치

   `pip install -U pip`

   `pip install -r requirements.txt`

## 2) Flow Chart

```mermaid
flowchart LR
  subgraph Client["사용자 인터페이스"]
    UI["Agent UI (추후) 또는 MCP Inspector"]
  end

  subgraph Agent["AI Agent (추후 연결)"]
    Planner["NLU / Planner\n(의도 파악·파라미터 추출·도구선택)"]
    Memory["Agent Memory / 로그(선택)"]
    Planner --- Memory
  end

  subgraph MCP["SoulSync-MCP 서버"]
    direction TB
    Tools["Tools\n- gmail_compose_draft\n- calendar_create_event_nl\n- ...(확장)"]
    Auth["OAuth 토큰/자격\n(secrets/, storage/)"]
    Tools --- Auth
  end

  subgraph External["외부 서비스"]
    GmailAPI["Gmail API"]
    GCalAPI["Google Calendar API"]
  end

  UI -->|"자연어 요청"| Agent
  Agent -->|"MCP 프로토콜 (JSON-RPC/STDIO)"| MCP
  MCP -->|"Tool 실행"| Tools
  Tools -->|"OAuth2 호출"| GmailAPI
  Tools -->|"OAuth2 호출"| GCalAPI
  GmailAPI --> Tools
  GCalAPI --> Tools
  Tools --> MCP
  MCP --> Agent
  Agent -->|"요약/결과"| UI

```

## 3) Google Cloud 설정 ( Calendar & Gmail )

#### 3-1) API 활성화
- Google Cloud Console → API 및 서비스 → 라이브러리
- Google Calendar API
- Gmail API
- 추후 필요한 API enable하여 추가
  
#### 3-2) OAuth 동의화면
- 사용자 유형 : 외부(External). 개인이 사용할 경우
- 게시 상태: 테스트 중(Testing)
- 테스트 사용자: 본인 Gmail 추가 → 저장
- Scope 설정

  아래 사진과 같이 설정
  
  <img width="729" height="838" alt="image" src="https://github.com/user-attachments/assets/25a547ac-8256-4c08-8d5a-36679c6377cd" />

  '범위 추가 또는 삭제' 선택

   Calendar: https://www.googleapis.com/auth/calendar.events

   Gmail: https://www.googleapis.com/auth/gmail.compose
  
  <img width="608" height="110" alt="image" src="https://github.com/user-attachments/assets/12e3f237-6e63-4109-a679-4562e885b110" />
  
#### 3-3) OAuth 클라이언트 ID
- API 및 서비스 → 사용자 인증 정보
- OAuth 클라이언트 ID 만들기
- **애플리케이션 유형 : 데스크톱 앱** - JSON 최상위 키 "installed" ( 유형 따라 다르나, 현재 개발한 프로젝트 상에서는 앱으로만 작동 )
- 생성 후 **JSON 다운로드** 후 이름 변경하여 secrets 폴더에 저장 : gcal_credentials.json / gmail_credentials.json


  
## 4) OAuth 토큰 발급

1) venv 활성화 상태에서 명령어 입력

- Gmail 초안 작성

   `python -c "from src.mcp_server.auth import ensure_credentials; from src.mcp_server.config import GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, GMAIL_SCOPES; c=ensure_credentials(GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, GMAIL_SCOPES); print('GMAIL token ->', GMAIL_TOKEN_PATH); print('Scopes:', getattr(c,'scopes',None))"`

- Gmail 전송

   `python -c "import base64;from email.mime.text import MIMEText;from googleapiclient.discovery import build;from google_auth_oauthlib.flow import InstalledAppFlow;from google.oauth2.credentials import Credentials;from email.utils import formataddr;from email.header import Header;import os;CREDS='secrets/gmail_credentials.json';TOKEN='storage/gmail_token.json';SCOPES=['https://www.googleapis.com/auth/gmail.compose'];creds=None;import pathlib
if os.path.exists(TOKEN): creds=Credentials.from_authorized_user_file(TOKEN, SCOPES)
if not creds or not creds.valid or not set(SCOPES).issubset(set(getattr(creds,'scopes',[]) or [])):
    flow=InstalledAppFlow.from_client_secrets_file(CREDS, SCOPES);creds=flow.run_local_server(port=0);open(TOKEN,'w',encoding='utf-8').write(creds.to_json())
service=build('gmail','v1',credentials=creds)
msg=MIMEText('한 줄 테스트 본문입니다.','plain','utf-8')
msg['To']=formataddr((str(Header('받는사람','utf-8')),'your.real.address@gmail.com'))
msg['Subject']=str(Header('한 줄 테스트','utf-8'))
raw=base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
print(service.users().messages().send(userId='me',body={'raw':raw}).execute())"`

   your.real.address@gmail.com에 실제 이메일 주소값 작성. 바로 전송됨.
  
- Gcal

   `python -c "from src.mcp_server.auth import ensure_credentials; from src.mcp_server.config import GCAL_CREDENTIALS_PATH, GCAL_TOKEN_PATH, GCAL_SCOPES; c=ensure_credentials(GCAL_CREDENTIALS_PATH, GCAL_TOKEN_PATH, GCAL_SCOPES); print('GCAL token ->', GCAL_TOKEN_PATH); print('Scopes:', getattr(c,'scopes',None))"`
 
2) 팝업창으로 뜨는 링크에서 권한 확인


3) storage폴더에 `gcal_token.json` / `gmail_token.json` 생성됨
   

## 5) MCP Inspector 실행 ( STDIO 연결 )
#### 5-1) Inspector 켜기
- 실행 전, Node.js 설치
  
   `npx @modelcontextprotocol/inspector`

#### 5-2) 연결 설정 (좌측 패널)
- Transport Type : `STDIO`
- Command : `C:\SoulSync-MCP\.venv\Scripts\python.exe`
- Arguments : `run_mcp_stdio.py`
- Working Directory : `C:\SoulSync-MCP`
- Environment Variables
  
  `GCAL_CREDENTIALS_PATH` = `secrets/gcal_credentials.json`
  
  `GMAIL_CREDENTIALS_PATH` = `secrets/gmail_credentials.json`
  
  `GCAL_TOKEN_PATH`       = `storage/gcal_token.json`
  
  `GMAIL_TOKEN_PATH`      = `storage/gmail_token.json`
  
  `TZ`                    = `Asia/Seoul`

좌상단 Connect(▶) → 왼쪽에 Tools 목록이 보이면 연결 완료.



## 6) Tool Test

#### 6-1) Calender_create_event_nl

     datetime_text: `2025-08-27 15:00`
  
     duration_min: `60`
  
     reason: `불안 관리 세션`
  
     timezone: `Asia/Seoul`
     
   Run Tool → id, htmlLink 확인

#### 6-2) gmail_compose_draft

     to: `you@example.com`
  
     subject: `TEST`
  
     body: `test`
  
   Run Tool → 초안 id, messageId 확인

---

## 7) Mail 보내기 Flow Chart

```mermaid
sequenceDiagram
  actor User as 사용자
  participant UI as Agent UI / MCP Inspector
  participant Agent as AI Agent (추후)
  participant MCP as SoulSync-MCP
  participant Gmail as Gmail API

  User->>UI: "내일 회의 공지 이메일 만들어줘"
  UI->>Agent: 자연어 요청 전달
  Agent->>Agent: 의도 파악/파라미터 추출/도구 선택
  Agent->>MCP: tools.gmail_compose_draft(제목, 본문, 수신자)
  MCP->>Gmail: drafts.create (OAuth)
  Gmail-->>MCP: Draft ID/결과
  MCP-->>Agent: Tool 결과(초안 링크/상태)
  Agent-->>UI: 완료 안내 + 요약/링크
  UI-->>User: 결과 표시

```

## *) 구상도도

```mermaid
flowchart LR
  %% =========================
  %% SoulSync-MCP Component Diagram (LR, with 1→2→3)
  %% =========================

  %% --- Client ---
  subgraph Client["클라이언트"]
    U[사용자]
    UI[웹앱 / Chat UI<br/>감정 게이지 시각화]
    U -. 대화/저널 .-> UI
  end

  %% --- Backend ---
  subgraph Backend["SoulSync 서비스 백엔드"]
    ORCH["대화 오케스트레이터 LLM<br/>(Function-calling, Persona)"]
    SAFETY["안전성·위기 라우터<br/>(다중라벨 분류기 + 규칙)"]
    POLICY["윤리·정책 템플릿 엔진"]

    EMB["임베딩·대화분석기<br/>(한국어 Bi-encoder)"]
    RAG["개인화 메모리 / RAG<br/>(검색·인용)"]
    SCORE["감정 스코어러<br/>(프로토타입 결합 + EMA)"]

    SUM["세션 요약기"]
    PERS["페르소나 스타일러<br/>(4 캐릭터)"]
    AGENT["툴 액션 에이전트<br/>(파라미터 검증 포함)"]
  end

  %% --- MCP ---
  subgraph MCP["MCP 통합 계층"]
    MCPS["MCP 서버"]
    GMAIL["Gmail Tool"]
    GCAL["Google Calendar Tool"]
    HOSP["병원/클리닉 API"]
    CRISIS["지역 위기 리소스"]
  end

  %% --- Storage / Infra ---
  subgraph Storage["저장소·인프라"]
    VDB["벡터DB(감정표/대화로그/지식)"]
    LOG["감사 로그 / 대화 이력"]
    VAULT["시크릿 금고(자격증명)"]
  end

  %% -------- Flows --------
  UI <--> ORCH

  ORCH --> SAFETY
  SAFETY --> POLICY
  POLICY --> ORCH

  %% 1→2→3 파이프라인
  ORCH -- "(1) 대화로그 임베딩·분석" --> EMB
  ORCH -- "(2) 감정표·대화로그 벡터 비교" --> RAG
  RAG <--> VDB
  ORCH -- "(3) 게이지 산출" --> SCORE
  SCORE --> UI

  %% RAG 답변 생성/요약
  ORCH <--> RAG
  ORCH --> SUM
  SUM --> LOG

  %% 페르소나
  ORCH --> PERS

  %% MCP 툴 실행
  ORCH --> AGENT
  AGENT <--> MCPS
  MCPS --> GMAIL
  MCPS --> GCAL
  MCPS --> HOSP
  MCPS --> CRISIS
  MCPS --> VAULT

  ORCH --> LOG
  AGENT --> LOG

  %% -------- Styling --------
  classDef core fill:#1f77b4,stroke:#0b2a4a,stroke-width:1,color:#fff;
  classDef aux fill:#2ca02c,stroke:#0b2a4a,stroke-width:1,color:#fff;
  classDef infra fill:#9467bd,stroke:#2f1a45,stroke-width:1,color:#fff;

  class ORCH,AGENT,RAG core;
  class SAFETY,EMB,SCORE,SUM,PERS,POLICY aux;
  class MCPS,GMAIL,GCAL,HOSP,CRISIS,VDB,LOG,VAULT infra;

```
## *) 트러블슈팅

- `redirect_uri_mismatch` : 웹(Web) 클라이언트 JSON 사용 - GCP에서 데스크톱 앱(Installed) 으로 새로 만들고 `secrets/*.json` 교체

- `403 access_denied` : 동의화면에 계정 미등록 - 테스트 사용자에 본인 Gmail 추가

- `insufficientPermissions` : 토큰 스코프 부족 - `storage/*token.json 삭제` → 토큰 재승인

   ( 권한 꼬임 해소 Tip - `https://myaccount.google.com/permissions` 에서 기존 앱 권한 제거 → token.json 삭제 → 토큰 재승인 )

- `secrets/` `storage/*token.json` `.gitignore` Commit 금지

- JSON/토큰 교체 후에는 Inspector종료 후, 다시 시작
