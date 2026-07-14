import json
from pathlib import Path

JSON_PATH = "resources/json/raw_json/resonator_stats.json"

THUMBNAIL_DIR = Path("resources/images/thumbnails")
STANDING_DIR = Path("resources/images/standings")

thumbnail_map = {}
standing_map = {}

name_map = {
    "설지": "Baizhi",
    "산화": "Sanhua",
    "능양": "Lingyang",
    "절지": "Zhezhi",
    "유호": "Youhu",
    "카를로타": "Carlotta",
    "히유키": "Hiyuki",
    "루실라": "Lucilla",
    "치샤": "Chixia",
    "모르테피": "Mortefi",
    "앙코": "Encore",
    "장리": "Changli",
    "브렌트": "Brant",
    "루파": "Lupa",
    "갈브레나": "Galbrena",
    "모니에": "Mornye",
    "에이메스": "Aemeath",
    "데니아": "Denia",
    "방랑자·회절": "Rover",
    "방랑자·인멸": "Rover",
    "방랑자·기류": "Rover",
    "연무": "Yuanwu",
    "카카루": "Calcharo",
    "음림": "Yinlin",
    "상리요": "Xiangli Yao",
    "루미": "LUMI",
    "아우구스타": "Augusta",
    "복링": "Buling",
    "레베카": "Rebecca",
    "양양": "Yangyang",
    "알토": "Aalto",
    "감심": "Jianxin",
    "기염": "Jiyan",
    "샤콘": "Ciaccona",
    "카르티시아": "Cartethyia",
    "유노": "Iuno",
    "구원": "Qiuyuan",
    "시그리카": "Sigrika",
    "벨리나": "Verina",
    "금희": "Jinhsi",
    "파수인": "The Shorekeeper",
    "페비": "Phoebe",
    "젠니": "Zani",
    "린네": "Lynae",
    "루크·헤르센": "Luuk Herssen",
    "루시": "Lucy",
    "단근": "Danjin",
    "도기": "Taoqi",
    "카멜리아": "Camellya",
    "로코코": "Roccia",
    "칸타렐라": "Cantarella",
    "플로로": "Phrolova",
    "치사": "Chisa",
}

eng_to_kor = {v: k for k, v in name_map.items()}

# thumbnail 매핑
for file in THUMBNAIL_DIR.iterdir():
    if file.is_file():
        english_name = file.stem.replace("-thumbnail", "")

        korean_name = eng_to_kor.get(english_name, english_name)

        thumbnail_map[korean_name] = (
            f"resonator-thumbnail-images/{file.name}"
        )

# standing 매핑
for file in STANDING_DIR.iterdir():
    if file.is_file():
        english_name = file.stem.replace("-standing", "")

        korean_name = eng_to_kor.get(english_name, english_name)

        standing_map[korean_name] = (
            f"resonator-standing-images/{file.name}"
        )

# JSON 로드
with open(JSON_PATH, "r", encoding="utf-8") as f:
    resonators = json.load(f)

# 이미지 경로 추가
for resonator in resonators:
    name = resonator["name"]

    if name in thumbnail_map:
        resonator["thumbnail image"] = thumbnail_map[name]

    if name in standing_map:
        resonator["standing image"] = standing_map[name]

# 저장
with open("resources/json/transform/resonator_stats.json", "w", encoding="utf-8") as f:
    json.dump(resonators, f, ensure_ascii=False, indent=4)

print("완료")