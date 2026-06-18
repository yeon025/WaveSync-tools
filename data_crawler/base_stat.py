import requests
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)


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


def get_character_stats(name, url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    stats = extract_stats(soup)

    return {
        "name": name,
        "hp": stats.get("HP"),
        "attack": stats.get("공격력"),
        "defense": stats.get("방어력"),
    }


def main():
    character_urls = get_character_urls()

    results = []

    for name, url in character_urls.items():
        try:
            stats = get_character_stats(name, url)

            if stats:
                results.append(stats)

        except Exception as e:
            print(f"[실패] {name}: {e}")

    with open("json/character_stats.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"{len(results)}개 저장 완료")


if __name__ == "__main__":
    main()