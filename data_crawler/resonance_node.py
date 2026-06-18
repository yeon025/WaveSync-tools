import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)

html = requests.get(URL, headers=HEADERS).text
soup = BeautifulSoup(html, "html.parser")




def get_character_urls():
    traveler_names = ["방랑자·기류", "방랑자·회절", "방랑자·인멸"]
    traveler_idx = 0

    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    summary = soup.find(
        "summary",
        string=lambda s: s and "속성별" in s
    )

    if summary is None:
        raise ValueError("[ 속성별 ] 섹션을 찾을 수 없습니다.")

    attribute_section = summary.find_parent("details")

    character_urls = {}

    for link in attribute_section.select("a[href^='/w/']"):

        img = link.select_one("img[alt$='아이콘']")

        if img is None:
            continue

        if img.find_parent("noscript"):
            continue

        name = (
            img["alt"]
            .replace("명조 ", "")
            .replace(" 아이콘", "")
        )

        if name == "방랑자":
            name = traveler_names[traveler_idx]
            traveler_idx += 1

        href = link.get("href")

        if not href:
            continue

        character_urls[name] = "https://namu.wiki" + href

    return character_urls


def find_node(name, url):
    nodes = []

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for details in soup.find_all("details"):
        for table in details.find_all("table"):
            trs = table.find_all("tr")

            if len(trs) != 2:
                continue

            text = trs[1].get_text(" ", strip=True)

            if "증가" in text:
                nodes.append(text)

            if len(nodes) >= 4:
                break

        if len(nodes) >= 4:
            break

    if len(nodes) < 4:
        return None

    parsed = []

    for node in nodes:
        match = re.match(r"(.+?)\s+([\d.]+%)", node)

        if not match:
            return None

        node_type = match.group(1).rstrip("이가")
        value = match.group(2)

        parsed.append((node_type, value))

    return {
        "name": name,
        "outer_node_type": parsed[0][0],
        "outer_top_node_value": parsed[1][1],
        "outer_middle_node_value": parsed[0][1],
        "inner_node_type": parsed[2][0],
        "inner_top_node_value": parsed[3][1],
        "inner_middle_node_value": parsed[2][1],
    }



def main():
    character_urls = get_character_urls()

    results = []

    for name, url in character_urls.items():
        try:
            result = find_node(name, url)

            if result:
                results.append(result)

        except Exception as e:
            print(f"[오류] {name}: {e}")

    with open("json/resonance_nodes.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"{len(results)}개 저장 완료")


if __name__ == "__main__":
    main()