import os
from dotenv import load_dotenv

load_dotenv()

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8088"))

# Google OAuth JSON & Token paths
GCAL_CREDENTIALS_PATH = os.getenv("GCAL_CREDENTIALS_PATH", "secrets/gcal_credentials.json")
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "secrets/gmail_credentials.json")
GCAL_TOKEN_PATH = os.getenv("GCAL_TOKEN_PATH", "storage/gcal_token.json")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "storage/gmail_token.json")

# Scopes
GCAL_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
# (나중에 '보내기'까지 할 거면 추가)
# GMAIL_SCOPES = [
#   "https://www.googleapis.com/auth/gmail.compose",
#   "https://www.googleapis.com/auth/gmail.send",
# ]