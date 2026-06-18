import json

files = [
    "resources/json/raw_json/weapon/broadblade.json",
    "resources/json/raw_json/weapon/gauntlet.json",
    "resources/json/raw_json/weapon/pistols.json",
    "resources/json/raw_json/weapon/rectifier.json",
    "resources/json/raw_json/weapon/sword.json"
]

merged = []

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        merged.extend(json.load(f))

with open("resources/json/transform/weapon.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=4)

print("완료")