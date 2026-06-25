import json


ELEMENT_MAP = {
    "응결": "GLACIO",
    "용융": "FUSION",
    "전도": "CONDUCTO",
    "기류": "AERO",
    "회절": "SPECTRA",
    "인멸": "HAVOC"
}

with open("resources/json/transform/resonator_stats.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("resources/sql/resonator_master.sql", "w", encoding="utf-8") as f:
    for item in data:
        standing_image = item.get("standing image")

        standing_image_sql = (
            f"'{standing_image}'"
            if standing_image is not None
            else "NULL"
        )

        sql = (
            "INSERT INTO resonator_master "
            "(name, element, rarity, hp, attack, defense, release_version, thumbnail_image, standing_image)\n"
            "VALUES ("
            f"'{item['name']}', "
            f"'{ELEMENT_MAP.get(item['element'], item['element'])}', " 
            f"{item['rarity']}, "
            f"{item['hp']}, {item['attack']}, {item['defense']}, {item['release version']}, "
            f"'{item['thumbnail image']}', {standing_image_sql});\n\n"
        )

        f.write(sql)

print("resonator_master.sql 생성 완료")