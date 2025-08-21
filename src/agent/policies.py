from enum import Enum
class Policy(str, Enum):
    AUTO = "auto"      # 바로 실행
    CONFIRM = "confirm" # 확인 후 실행(외부 시스템)
    DRAFT = "draft"    # 초안만 생성(대외 송신)
