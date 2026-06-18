import json

def sql_number(value):
    if value is None:
        return "NULL"
    return value.replace("%", "")

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
            f"'{item['outer_node_type']}', "
            f"{sql_number(item['outer_top_node_value'])}, "
            f"{sql_number(item['outer_middle_node_value'])}, "
            f"'{item['inner_node_type']}', "
            f"{sql_number(item['inner_top_node_value'])}, "
            f"{sql_number(item['inner_middle_node_value'])}, "
            f"(SELECT id FROM resonator_master WHERE name = '{item['name']}')"
            ");\n\n"
        )

        f.write(sql)

print("resonator_node.sql 생성 완료")