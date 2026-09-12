from util import fetch_soup, crawl_character_urls, save_json


def extract_echo_stats(soup):
    """"에코 옵티마이즈" 섹션의 스탯 유형명만 추출한다(수치 제외).
    해시 class명 대신 "부음 속성" 다음 형제 tr을 기준으로 삼는다."""
    label_tr = None

    for strong in soup.find_all("strong"):
        if "부음 속성" in strong.get_text(strip=True):
            label_tr = strong.find_parent("tr")
            break

    if label_tr is None:
        return []

    stat_tr = label_tr.find_next_sibling("tr")

    if stat_tr is None:
        return []

    echo_stats = []

    # 카드마다 <strong>이 두 개(유형명, 수치)씩 순서대로 나오므로, 짝수 인덱스만 유형명으로 취급한다.
    strongs = stat_tr.find_all("strong")

    for name_strong in strongs[0::2]:

        name = name_strong.get_text(strip=True)

        if not name:
            continue

        # placeholder 카드는 상위 요소에 style="display:none"이 적용되어 있다.
        if name_strong.find_parent(style=lambda s: s and "display:none" in s):
            continue

        if name not in echo_stats:
            echo_stats.append(name)

    return echo_stats


def crawl_character(name, url):
    print(f"{name} 추출 시작")

    soup = fetch_soup(url)

    echo_stats = extract_echo_stats(soup)

    return {
        "name": name,
        "echo_stats": echo_stats,
    }


def main():
    character_urls = crawl_character_urls()

    results = []

    for name, url in character_urls.items():
        try:
            result = crawl_character(name, url)

            results.append(result)

        except Exception as e:
            print(f"[실패] {name}: {e}")

    save_json(results, "resources/json/echo_stats.json")

    print(f"{len(results)}개 저장 완료")


if __name__ == "__main__":
    main()
