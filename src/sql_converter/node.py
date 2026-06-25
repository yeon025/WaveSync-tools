import json

def sql_number(value):
    if value is None:
        return "NULL"
    return value.replace("%", "")


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
    "치료 효과 보너스": "HEALING_BONUS"
}


with open("resources/json/raw_json/resonance_nodes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("resources/sql/resonance_node_master.sql", "w", encoding="utf-8") as f:
    for item in data:
        sql = (
            "INSERT INTO resonance_node_master ("
            "outer_node_type, outer_top_node_value, outer_middle_node_value, "
            "inner_node_type, inner_top_node_value, inner_middle_node_value, "
            "resonator_master_id"
            ")\n"
            "VALUES ("
            f"'{STAT_MAP.get(item['outer_node_type'], item['outer_node_type'])}', " 
            f"{sql_number(item['outer_top_node_value'])}, "
            f"{sql_number(item['outer_middle_node_value'])}, "
            f"'{STAT_MAP.get(item['inner_node_type'], item['inner_node_type'])}', " 
            f"{sql_number(item['inner_top_node_value'])}, "
            f"{sql_number(item['inner_middle_node_value'])}, "
            f"(SELECT id FROM resonator_master WHERE name = '{item['name']}')"
            ");\n\n"
        )

        f.write(sql)

print("resonance_node.sql 생성 완료")