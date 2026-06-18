import json

with open("json/transform/resonator_stats.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("sql/resonator_master.sql", "w", encoding="utf-8") as f:
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
            f"'{item['name']}', '{item['element']}', {item['rarity']}, "
            f"{item['hp']}, {item['attack']}, {item['defense']}, {item['release version']},"
            f"'{item['thumbnail image']}', {standing_image_sql});\n\n"
        )

        f.write(sql)

print("resonator_master.sql 생성 완료")