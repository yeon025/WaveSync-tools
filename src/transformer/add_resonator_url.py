import json
from pathlib import Path

JSON_PATH = "resources/json/resonator_stats.json"

THUMBNAIL_DIR = Path("resources/images/thumbnails")
STANDING_DIR = Path("resources/images/standings")

thumbnail_map = {}
standing_map = {}

# thumbnail 매핑
for file in THUMBNAIL_DIR.iterdir():
    if file.is_file():
        english_name = file.stem.replace("-thumbnail", "")

        thumbnail_map[english_name.strip()] = (
            f"resonator-thumbnail-images/{file.name}"
        )

# standing 매핑
for file in STANDING_DIR.iterdir():
    if file.is_file():
        english_name = file.stem.replace("-standing", "")

        standing_map[english_name.strip()] = (
            f"resonator-standing-images/{file.name}"
        )

# JSON 로드
with open(JSON_PATH, "r", encoding="utf-8") as f:
    resonators = json.load(f)

# 이미지 경로 추가
for resonator in resonators:
    name_eng = resonator["name_eng"]
    key = name_eng.strip()

    if key in thumbnail_map:
        resonator["thumbnail image"] = thumbnail_map[key]
    else:
        print(f"[경고] thumbnail image 없음: {name_eng}")

    if key in standing_map:
        resonator["standing image"] = standing_map[key]
    else:
        print(f"[경고] standing image 없음: {name_eng}")

# 저장
with open("resources/json/transform/resonator_stats.json", "w", encoding="utf-8") as f:
    json.dump(resonators, f, ensure_ascii=False, indent=4)

print("완료")
