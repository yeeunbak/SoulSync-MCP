# 로컬 실행 가이드 ( MCP : Google Calendar + Gmail )

### 요구사항
- Python 3.10+ (권장 3.11)
- Node.js LTS (npx 사용) → 명령어 node -v, npm -v 로 버전 확인



## 1) 가상환경설정

1) 레포 폴더로 이동
   
   `cd C:\SoulSync-MCP`

2) 가상환경 생성/활성화
   
   `python -m venv .venv`

   `.\.venv\Scripts\Activate.ps1`

3) 패키지 설치

   `pip install -U pip`

   `pip install -r requirements.txt`



## 2) Google Cloud 설정 ( Calendar & Gmail )

#### 2-1) API 활성화
- Google Cloud Console → API 및 서비스 → 라이브러리
- Google Calendar API
- Gmail API
- 추후 필요한 API enable하여 추가
  
#### 2-2) OAuth 동의화면
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
  
#### 2-3) OAuth 클라이언트 ID
- API 및 서비스 → 사용자 인증 정보
- OAuth 클라이언트 ID 만들기
- **애플리케이션 유형 : 데스크톱 앱** - JSON 최상위 키 "installed" ( 유형 따라 다르나, 현재 개발한 프로젝트 상에서는 앱으로만 작동 )
- 생성 후 **JSON 다운로드** 후 이름 변경하여 secrets 폴더에 저장 : gcal_credentials.json / gmail_credentials.json


  
## 3) OAuth 토큰 발급

1) venv 활성화 상태에서 명령어 입력

- Gmail : `python -c "from src.mcp_server.auth import ensure_credentials; from src.mcp_server.config import GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, GMAIL_SCOPES; c=ensure_credentials(GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, GMAIL_SCOPES); print('GMAIL token ->', GMAIL_TOKEN_PATH); print('Scopes:', getattr(c,'scopes',None))"`
  
- Gcal : `python -c "from src.mcp_server.auth import ensure_credentials; from src.mcp_server.config import GCAL_CREDENTIALS_PATH, GCAL_TOKEN_PATH, GCAL_SCOPES; c=ensure_credentials(GCAL_CREDENTIALS_PATH, GCAL_TOKEN_PATH, GCAL_SCOPES); print('GCAL token ->', GCAL_TOKEN_PATH); print('Scopes:', getattr(c,'scopes',None))"`
 
2) 팝업창으로 뜨는 링크에서 권한 확인

3) storage폴더에 gcal_token.json / gmail_token.json 생성됨
   

## 4) MCP Inspector 실행 ( STDIO 연결 )
#### 4-1) Inspector 켜기
- 실행 전, Node.js 설치
  
   `npx @modelcontextprotocol/inspector`

#### 4-2) 연결 설정 (좌측 패널)
- Transport Type : **STDIO**
- Command : **C:\SoulSync-MCP\.venv\Scripts\python.exe**
- Arguments : **run_mcp_stdio.py**
- Working Directory : C:\SoulSync-MCP
- Environment Variables
  
  `GCAL_CREDENTIALS_PATH` = `secrets/gcal_credentials.json`
  
  `GMAIL_CREDENTIALS_PATH` = `secrets/gmail_credentials.json`
  
  `GCAL_TOKEN_PATH`       = `storage/gcal_token.json`
  
  `GMAIL_TOKEN_PATH`      = `storage/gmail_token.json`
  
  `TZ`                    = `Asia/Seoul`

좌상단 Connect(▶) → 왼쪽에 Tools 목록이 보이면 연결 완료.



## 5) Tool Test
#### 5-1) Calender_create_event_nl

     datetime_text: `2025-08-27 15:00`
  
     duration_min: `60`
  
     reason: `불안 관리 세션`
  
     timezone: `Asia/Seoul`
     
   Run Tool → id, htmlLink 확인

#### 5-2) gmail_compose_draft

     to: `you@example.com`
  
     subject: `TEST`
  
     body: `test`
  
   Run Tool → 초안 id, messageId 확인
  
