import re

from util import fetch_soup, crawl_character_urls, save_json


def find_node(name, url):
    print(f"{name} 추출 시작")

    nodes = []

    soup = fetch_soup(url)

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
    character_urls = crawl_character_urls()

    results = []

    for name, url in character_urls.items():
        try:
            result = find_node(name, url)

            if result:
                results.append(result)

        except Exception as e:
            print(f"[오류] {name}: {e}")

    save_json(results, "resources/json/resonance_nodes.json")

    print(f"{len(results)}개 저장 완료")


if __name__ == "__main__":
    main()
