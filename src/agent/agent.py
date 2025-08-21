from .router import route, invoke

def run_cli():
    user_id = "demo-user"
    print("SoulSync Agent CLI. 예) '기분 -1 / 불안 7 기록', '저널에 \"면접 걱정\" 저장', '호흡 가이드 시작', '도와줘', '다음 주 수요일 3시에 상담 예약 잡아줘', '상담사에게 이메일 초안'")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            break
        if not text:
            continue
        out = route(user_id, text)
        t = out.get("type")
        if t == "auto_done":
            print(f"[AUTO] {out['tool']} 실행 완료 → 결과: {out['result']}")
        elif t == "confirm_required":
            print(f"[CONFIRM] {out['tool']} 실행 준비됨. 인자: {out['args']}")
            yn = input("실행할까요? (y/n) ").lower()
            if yn.startswith("y"):
                try:
                    result = invoke(out["tool"], out["args"])
                    print(f"[CONFIRM→RUN] 실행 완료 → 결과: {result}")
                except Exception as e:
                    print(f"[ERROR] 실행 실패: {e}")
            else:
                print("취소했어요.")
        elif t == "draft":
            print(f"[DRAFT] 초안 생성됨: {out['draft']}")
        else:
            print(out.get("content"))

if __name__ == "__main__":
    run_cli()
