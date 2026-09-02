import json

files = [
    "resources/json/broadblade.json",
    "resources/json/gauntlet.json",
    "resources/json/pistols.json",
    "resources/json/rectifier.json",
    "resources/json/sword.json"
]

merged = []

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        merged.extend(json.load(f))

with open("resources/json/transform/weapon.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=4)