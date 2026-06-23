import json

def sql_number(value):
    if value is None:
        return "NULL"
    return value.replace("%", "")


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
    "치료 효과 보너스": "healing_bonus"
}


with open("resources/json/raw_json/resonance_nodes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("resources/sql/resonator_node_master.sql", "w", encoding="utf-8") as f:
    for item in data:
        sql = (
            "INSERT INTO resonator_node_master ("
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

print("resonator_node.sql 생성 완료")