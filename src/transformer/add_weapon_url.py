import json
from pathlib import Path

JSON_PATH = "resources/json/transform/weapon.json"

WEAPON_DIR = Path("resources/images/weapons")

weapon_map = {}

# weapon 매핑
for file in WEAPON_DIR.iterdir():
    if file.is_file():
        weapon_map[file.stem] = (
            f"weapon-images/{file.name}"
        )



# JSON 로드
with open(JSON_PATH, "r", encoding="utf-8") as f:
    weapons = json.load(f)

# 이미지 경로 추가
for weapon in weapons:
    name = weapon["weapon_name"]

    if name in weapon_map:
        weapon["weapon_image"] = weapon_map[name]


# 저장
with open("resources/json/transform/weapon.json", "w", encoding="utf-8") as f:
    json.dump(weapons, f, ensure_ascii=False, indent=4)

print("완료")