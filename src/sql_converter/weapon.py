import json

with open("resources/json/transform/weapon.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def sql_text(value):
    return f"'{value}'" if value is not None else "NULL"

def sql_number(value):
    if value is None:
        return "NULL"
    return value.replace("%", "")

with open("resources/sql/weapon_master.sql", "w", encoding="utf-8") as f:
    for item in data:
        sql = (
            "INSERT INTO weapon_master "
            "(name, attack_value, main_type, main_value, refine_type,\n"
            "refine_1_value, refine_2_value, refine_3_value, refine_4_value, refine_5_value, image)\n"
            "VALUES ("
            f"'{item['weapon_name']}', "
            f"{item['attack_value']}, "
            f"'{item['main_type']}', "
            f"{sql_number(item['main_value'])}, "
            f"{sql_text(item.get('refine_type'))}, "
            f"{sql_number(item.get('refine_1_value'))}, "
            f"{sql_number(item.get('refine_2_value'))}, "
            f"{sql_number(item.get('refine_3_value'))}, "
            f"{sql_number(item.get('refine_4_value'))}, "
            f"{sql_number(item.get('refine_5_value'))}, "
            f"'{item['weapon_image']}'"
            ");\n\n"
        )

        f.write(sql)

print("weapon_master.sql 생성 완료")