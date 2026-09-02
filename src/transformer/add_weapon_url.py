import json
import shutil
from pathlib import Path

JSON_PATH = "resources/json/transform/weapon.json"
WEAPON_DIR = Path("resources/images/weapons")
NEW_WEAPON_DIR = Path("resources/images/new_weapons")

NEW_WEAPON_DIR.mkdir(parents=True, exist_ok=True)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    weapons = json.load(f)

for idx, weapon in enumerate(weapons, start=1):
    old_path = WEAPON_DIR / f"{weapon['weapon_name']}.webp"

    if not old_path.exists():
        print(f"이미지를 찾을 수 없습니다: {old_path.name}")
        continue

    new_name = f"{idx}.webp"
    new_path = NEW_WEAPON_DIR / new_name

    shutil.copy2(old_path, new_path)  # rename -> copy2로 변경 (원본 유지)

    weapon["weapon_image"] = f"weapon-images/{new_name}"

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(weapons, f, ensure_ascii=False, indent=4)