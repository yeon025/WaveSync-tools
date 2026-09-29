import json


SCALING_STAT_MAP = {
    "공격력 백분율": "attack",
    "HP 백분율": "hp",
    "방어력 백분율": "defense"
}

DMG_TYPE_MAP = {
    "공명 스킬 피해 보너스": "resonance_skill_damage_bonus",
    "공명 해방 피해 보너스": "resonance_liberation_damage_bonus",
    "일반 공격 피해 보너스": "basic_attack_damage_bonus",
    "강공격 피해 보너스": "heavy_attack_damage_bonus"
}

EXCLUDED_NAMES = {
    "설지", "수수", "복링", "벨리나", "파수인", "모니에"
}


def sql_text(value):
    if value is None:
        return "NULL"
    return f"'{value}'"


with open("resources/json/echo_stats.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("resources/sql/resonator_damage_master.sql", "w", encoding="utf-8") as f:
    for item in data:
        if item["name"] in EXCLUDED_NAMES:
            print(f"제외됨: {item['name']}")
            continue

        echo_stats = item["echo_stats"]

        scaling_stat = next(
            (SCALING_STAT_MAP[stat] for stat in echo_stats if stat in SCALING_STAT_MAP),
            None
        )
        dmg_types = [DMG_TYPE_MAP[stat] for stat in echo_stats if stat in DMG_TYPE_MAP]

        if scaling_stat is None:
            print(f"건너뜀: {item['name']} (scaling_stat=None, relevant_dmg_type={dmg_types})")
            continue

        if not dmg_types:
            dmg_types = [None]

        for dmg_type in dmg_types:
            sql = (
                "INSERT INTO resonator_damage_master "
                "(relevant_damage_type, scaling_stat, resonator_master_id)\n"
                "VALUES ("
                f"{sql_text(dmg_type)}, '{scaling_stat}', (SELECT id FROM resonator_master WHERE name = '{item['name']}')"
                ");\n\n"
            )

            f.write(sql)

print("resonator_damage_master.sql 생성 완료")
