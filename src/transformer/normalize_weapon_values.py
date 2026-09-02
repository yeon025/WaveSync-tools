"""
무기 데이터(JSON) 정제 스크립트.

처리 내용:
    1. "refine_type" 값 끝의 조사(은/는/이/가)를 제거
       예: "공격력이" -> "공격력", "체력은" -> "체력"
    2. "main_value", "refine_1_value" ~ "refine_5_value" 값의 "%" 문자를 제거
       예: "12%" -> "12", "48.6%" -> "48.6"
    3. (1)(2) 이후, "refine_type" 이 순수 스탯명이 아니라 발동 조건이 포함된
       문장인 경우 해당 무기의 refine 관련 키를 모두 제거
       예: "변주 스킬 발동 시, 자신의 공격력" + refine_value  ->  두 키 모두 삭제

대상 파일:
    기본값은 아래 INPUT_PATH 상수. 명령줄 인자로도 지정할 수 있다.

        python src/transformer/normalize_weapon_values.py
        python src/transformer/normalize_weapon_values.py path/to/weapon.json
        python src/transformer/normalize_weapon_values.py path/to/weapon.json -o out.json

    -o/--output 를 주지 않으면 원본 파일을 덮어쓴다.
"""

import argparse
import json
import re

INPUT_PATH = "resources/json/transform/weapon.json"

JOSA = ("은", "는", "이", "가")

# refine 값 관련 키 (% 제거 대상이자, 조건절 감지 시 삭제 대상)
REFINE_VALUE_KEYS = (
    "refine_value",
    "refine_1_value",
    "refine_2_value",
    "refine_3_value",
    "refine_4_value",
    "refine_5_value",
)

# % 제거 대상 (main_value 는 삭제 대상이 아니므로 별도)
PERCENT_KEYS = ("main_value",) + REFINE_VALUE_KEYS

# 시간/조건을 나타내는 표현 (하나라도 포함되면 조건절로 간주)
CONDITION_KEYWORDS = (
    "발동 시",
    "발동 후",
    "발동시",
    "발동후",
    "입힐 시",
    "초 내",
    "초내",
    "이내",
    "마다",
    "동안",
    "시전",
    "경우",
    "할 때"
)

# 위 키워드가 잡지 못하는 조건 문장을 위한 보조 정규식
#  - "N초" 처럼 숫자+초 조합
#  - 공백 뒤의 "중" (예: "전투 중", "지속 시간 중") — "집중" 같은 단어는 제외
#  - 발동/시전/스택/처치/명중/적중/피격 등 조건 트리거 어휘
CONDITION_PATTERN = re.compile(
    r"발동|시전|\d+\s*초|(?<=\s)중|스택|처치|명중|적중|피격"
)


def strip_josa(value):
    if isinstance(value, str) and value.endswith(JOSA):
        return value[:-1]
    return value


def strip_percent(value):
    if isinstance(value, str):
        return value.replace("%", "")
    return value


def is_conditional_refine_type(value):
    """refine_type 이 순수 스탯명이 아니라 조건절을 포함하면 True."""
    if not isinstance(value, str):
        return False

    if any(keyword in value for keyword in CONDITION_KEYWORDS):
        return True

    return bool(CONDITION_PATTERN.search(value))


def normalize(weapons):
    """1) 조사 제거, 2) % 제거."""
    for weapon in weapons:
        if "refine_type" in weapon:
            weapon["refine_type"] = strip_josa(weapon["refine_type"])

        for key in PERCENT_KEYS:
            if key in weapon:
                weapon[key] = strip_percent(weapon[key])

    return weapons


def drop_conditional_refine(weapons):
    """3) refine_type 이 조건절이면 refine 관련 키 전부 제거."""
    for weapon in weapons:
        refine_type = weapon.get("refine_type")

        if not is_conditional_refine_type(refine_type):
            continue

        removed_keys = []

        if "refine_type" in weapon:
            del weapon["refine_type"]
            removed_keys.append("refine_type")

        for key in REFINE_VALUE_KEYS:
            if key in weapon:
                del weapon[key]
                removed_keys.append(key)

        name = weapon.get("weapon_name", "(이름 없음)")
        print(
            f"[조건절 감지] {name}: \"{refine_type}\" -> 키 제거 "
            f"({', '.join(removed_keys)})"
        )

    return weapons


def main():
    parser = argparse.ArgumentParser(description="무기 JSON 값 정제")
    parser.add_argument(
        "input",
        nargs="?",
        default=INPUT_PATH,
        help=f"대상 JSON 파일 경로 (기본값: {INPUT_PATH})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="출력 파일 경로 (미지정 시 입력 파일을 덮어씀)",
    )
    args = parser.parse_args()

    output_path = args.output or args.input

    with open(args.input, "r", encoding="utf-8") as f:
        weapons = json.load(f)

    normalize(weapons)
    drop_conditional_refine(weapons)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(weapons, f, ensure_ascii=False, indent=4)

    print(f"정제 완료: {args.input} -> {output_path} ({len(weapons)}건)")


if __name__ == "__main__":
    main()
