import json
from pathlib import Path

JSON_PATH = "resources/json/transform/weapon.json"
WEAPON_DIR = Path("resources/images/weapons")

# JSON 로드
with open(JSON_PATH, "r", encoding="utf-8") as f:
    weapons = json.load(f)

# JSON 순서대로 이미지 이름 변경
for idx, weapon in enumerate(weapons, start=1):
    old_path = WEAPON_DIR / f"{weapon['weapon_name']}.webp"

    if not old_path.exists():
        print(f"이미지를 찾을 수 없습니다: {old_path.name}")
        continue

    new_name = f"{idx}.webp"
    new_path = WEAPON_DIR / new_name

    old_path.rename(new_path)

    # JSON에도 경로 저장
    weapon["weapon_image"] = f"weapon-images/{new_name}"

# 저장
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(weapons, f, ensure_ascii=False, indent=4)

print("완료")