import json


STAT_MAP = {
    "HP": "hp",
    "공격력": "attack",
    "방어력": "defense",
    "공명 효율": "energy_regen",
    "크리티컬": "critical_rate",
    "크리티컬 확률": "critical_rate",
    "크리티컬 피해": "critical_damage",
    "공명 스킬 피해 보너스": "resonance_skill_damage_bonus",
    "일반 공격 피해 보너스": "basic_attack_damage_bonus",
    "강공격 피해 보너스": "heavy_attack_damage_bonus",
    "공명 해방 피해 보너스": "resonance_liberation_damage_bonus",
    "응결 피해 보너스": "glacio_damage_bonus",
    "용융 피해 보너스": "fusion_damage_bonus",
    "전도 피해 보너스": "conducto_damage_bonus",
    "기류 피해 보너스": "aero_damage_bonus",
    "회절 피해 보너스": "spectra_damage_bonus",
    "인멸 피해 보너스": "havoc_damage_bonus",
    "치료 효과 보너스": "healing_bonus",
    "전체 속성 피해 보너스": "all_attribute_damage_bonus",
    "일반 공격과 강공격 피해 보너스": "basic_attack_damage_bonus/heavy_attack_damage_bonus"
}



with open("resources/json/transform/weapon.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def sql_text(value):
    if value is None:
        return "NULL"

    mapped = STAT_MAP.get(value, value)
    return f"'{mapped}'"

def sql_number(value):
    if value is None:
        return "NULL"
    return value.replace("%", "")

with open("resources/sql/weapon_master.sql", "w", encoding="utf-8") as f:
    for item in data:
        sql = (
            "INSERT INTO weapon_master "
            "(weapon_name, attack_value, main_type, main_value, refine_type,\n"
            "refine_1_value, refine_2_value, refine_3_value, refine_4_value, refine_5_value, weapon_image)\n"
            "VALUES ("
            f"'{item['weapon_name']}', "
            f"{item['attack_value']}, "
            f"'{STAT_MAP.get(item['main_type'], item['main_type'])}', " 
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