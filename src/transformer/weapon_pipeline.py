"""SCRIPTS를 순서대로 실행하고, 실패하면 즉시 중단한다."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 이 파일 기준 경로
SCRIPT_DIR = Path(__file__).resolve().parent
# 프로젝트 루트 (스크립트들이 상대 경로를 프로젝트 루트 기준으로 사용함)
PROJECT_ROOT = SCRIPT_DIR.parent.parent

SCRIPTS = [
    "merge_weapon.py",
    "separate_refine.py",
    "normalize_weapon_values.py",
    "add_weapon_url.py",
]


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def run_script(index: int, total: int, script_name: str) -> None:
    script_path = SCRIPT_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"스크립트를 찾을 수 없습니다: {script_path}")

    log(f"({index}/{total}) 실행 시작: {script_name}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{script_name} 이(가) 종료 코드 {result.returncode} 로 실패했습니다."
        )

    log(f"({index}/{total}) 정상 종료: {script_name}")


def main() -> None:
    total = len(SCRIPTS)
    log(f"transformer 파이프라인 시작 (총 {total}개 스크립트)")
    log(f"작업 디렉터리: {PROJECT_ROOT}")

    for i, script_name in enumerate(SCRIPTS, start=1):
        try:
            run_script(i, total, script_name)
        except Exception as exc:
            log(f"에러 발생 - 파이프라인을 중단합니다: {exc}")
            sys.exit(1)

    log("모든 스크립트가 정상적으로 완료되었습니다.")


if __name__ == "__main__":
    main()
