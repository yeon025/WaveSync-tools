from util import fetch_soup, crawl_character_urls, save_json
import re


def extract_stats(soup):
    stats = {}

    targets = {"HP", "공격력", "방어력"}

    for strong in soup.select("strong"):

        name = strong.get_text(strip=True)

        if name not in targets:
            continue

        if name in stats:
            continue

        row = strong.find_parent("div").parent

        cols = row.find_all("div", recursive=False)

        if len(cols) < 2:
            continue

        stats[name] = cols[1].get_text(strip=True)

        if stats.keys() >= targets:
            break

    return stats


def crawl_character(name, url):
    print(f"{name} 추출 시작")

    soup = fetch_soup(url)

    stats = extract_stats(soup)

    element = extract_element(soup)

    if "방랑자" in name:
        name_eng = "Rover"
    else:
        name_eng = find_English_name(url)

    return {
        "name": name,
        "name_eng": name_eng,
        "element": element,
        "hp": stats.get("HP"),
        "attack": stats.get("공격력"),
        "defense": stats.get("방어력"),
    }


def extract_element(soup):
    """
    공명자 문서에서 "속성: " 뒤에 오는 속성 값을 추출한다.
    "속성:" 레이블을 찾지 못하면 None을 반환한다.
    """

    for strong in soup.find_all("strong"):
        text = strong.get_text(strip=True)

        match = re.match(r"속성\s*[:：]\s*(.+)", text)

        if match:
            return match.group(1).strip()

    return None


def find_English_name(wiki_url: str) -> str:
    """공명자 문서에서 영문 이름을 추출해서 반환한다."""
    soup = fetch_soup(wiki_url)

    strong = soup.select_one("strong:has(ruby)")

    english_name = strong.get_text(" ", strip=True).split("|")[-1].strip()

    return english_name


def main():
    character_urls = crawl_character_urls()

    results = []

    for name, url in character_urls.items():
        try:
            stats = crawl_character(name, url)

            results.append(stats)

        except Exception as e:
            print(f"[실패] {name}: {e}")

    save_json(results, "resources/json/resonator_stats.json")

    print(f"{len(results)}개 저장 완료")


if __name__ == "__main__":
    main()
