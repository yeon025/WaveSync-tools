import json


STAT_MAP = {
    "HP": "HP_PERCENT",
    "공격력": "ATTACK_PERCENT",
    "방어력": "DEFENSE_PERCENT",
    "공명 효율": "ENERGY_REGEN",
    "크리티컬": "CRITICAL_RATE",
    "크리티컬 확률": "CRITICAL_RATE",
    "크리티컬 피해": "CRITICAL_DAMAGE",
    "공명 스킬 피해 보너스": "RESONANCE_SKILL_DAMAGE_BONUS",
    "일반 공격 피해 보너스": "BASIC_ATTACK_DAMAGE_BONUS",
    "강공격 피해 보너스": "HEAVY_ATTACK_DAMAGE_BONUS",
    "공명 해방 피해 보너스": "RESONANCE_LIBERATION_DAMAGE_BONUS",
    "응결 피해 보너스": "GLACIO_DAMAGE_BONUS",
    "용융 피해 보너스": "FUSION_DAMAGE_BONUS",
    "전도 피해 보너스": "CONDUCTO_DAMAGE_BONUS",
    "기류 피해 보너스": "AERO_DAMAGE_BONUS",
    "회절 피해 보너스": "SPECTRA_DAMAGE_BONUS",
    "인멸 피해 보너스": "HAVOC_DAMAGE_BONUS",
    "치료 효과 보너스": "HEALING_BONUS",
    "전체 속성 피해 보너스": "ALL_ATTRIBUTE_DAMAGE_BONUS",
    "일반 공격과 강공격 피해 보너스": "BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS"
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
            "(name, attack_value, main_type, main_value, refine_type,\n"
            "refine_1_value, refine_2_value, refine_3_value, refine_4_value, refine_5_value, image)\n"
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