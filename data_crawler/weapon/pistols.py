import requests
from bs4 import BeautifulSoup
import json


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EB%AC%B4%EA%B8%B0/%EA%B6%8C%EC%B4%9D"
)

html = requests.get(URL, headers=HEADERS).text
soup = BeautifulSoup(html, "html.parser")

weapons = []

for tbody in soup.find_all("tbody"):
    trs = tbody.find_all("tr", recursive=False)

    if len(trs) != 2:
        continue
    


    # 무기명
    first_tr = trs[0]

    title = first_tr.select_one(
        'div[style*="border-left:5px solid"] > strong'
    )

    if not title:
        continue

    weapon_name = title.get_text(strip=True)

    # 능력치
    second_tr = trs[1]

    texts = list(trs[1].stripped_strings)

    if len(texts) < 4:
        continue

    stat1_name, stat1_value, stat2_name, stat2_value = texts[:4]
    refine_type = texts[5]
    refine_value = texts[6]

    weapons.append({
        "weapon_name": weapon_name,
        "attack_value": stat1_value,
        "main_type": stat2_name,
        "main_value": stat2_value,
        "refine_type": refine_type,
        "refine_value": refine_value
    })



with open("datas/pistols.json", "w", encoding="utf-8") as f:
    json.dump(
        weapons,
        f,
        ensure_ascii=False,
        indent=4
    )

print(f"{len(weapons)}개 권총 저장 완료")