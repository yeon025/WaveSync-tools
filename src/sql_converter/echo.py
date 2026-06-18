from pathlib import Path

image_dir = Path("resources/images/echoes")

with open("resources/sql/echo_master.sql", "w", encoding="utf-8") as f:
    for image_file in sorted(image_dir.glob("*.png")):
        name = image_file.stem
        image_path = f"echo-images/{image_file.name}"

        sql = (
            "INSERT INTO echo_master (name, image) "
            f"VALUES ('{name}', '{image_path}');\n\n"
        )

        f.write(sql)

print("echo_master.sql 생성 완료")