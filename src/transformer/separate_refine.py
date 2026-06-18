import json

with open("resources/json/transform/weapon.json", "r", encoding="utf-8") as f:
    weapons = json.load(f)

for weapon in weapons:
    refine_value = weapon.get("refine_value")

    if refine_value:
        values = refine_value.split("/")

        for i, value in enumerate(values, start=1):
            weapon[f"refine_{i}_value"] = value

        del weapon["refine_value"]

with open("resources/json/transform/weapon.json", "w", encoding="utf-8") as f:
    json.dump(weapons, f, ensure_ascii=False, indent=4)

print("완료")