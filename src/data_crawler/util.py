"""data_crawler 공통 유틸리티.

base_stat / resonance_node / weapon 크롤러에서 반복적으로 쓰이는
상수, HTTP 요청/파싱, 공명자 문서 수집, 무기 능력치 파싱, JSON 저장 로직을 모아둔다.
"""

import json
import re
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)

# 공명자 속성은 이 6종으로 고정되어 있다.
ATTRIBUTE_NAMES = ["응결", "용융", "전도", "기류", "회절", "인멸"]

# namu.wiki가 동명이인 문서와 구분하기 위해 이름에 붙이는 표기.
# 예: "산화(명조: 워더링 웨이브)" -> "산화"
_DISAMBIGUATION_SUFFIX = re.compile(r"\(명조:\s*워더링\s*웨이브\)")


def fetch_soup(url: str) -> BeautifulSoup:
    """URL을 GET 요청하고 응답 HTML을 BeautifulSoup 객체로 파싱해서 반환한다."""
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


def _find_attribute_heading(soup: BeautifulSoup):
    """"3. 속성" 섹션의 <h2> 헤딩을 찾는다 (섹션 번호는 하드코딩하지 않고
    id="속성" span, 없으면 id="s-3" 앵커로 폴백). 못 찾으면 None."""
    for heading in soup.find_all("h2"):
        if heading.find("span", id="속성"):
            return heading

        if heading.find("a", id="s-3"):
            return heading

    return None


def crawl_character_urls() -> dict[str, str]:
    """"3. 속성" 섹션 아래 속성별 표(이름 tr 다음 형제 tr에 링크)에서 공명자
    이름 -> 나무위키 문서 URL 딕셔너리를 만든다. "방랑자"는 속성 구분과
    무관하게 문서 전체 등장 순서대로 전도/기류/회절/인멸로 구분한다."""
    rover_names = ["방랑자·전도", "방랑자·기류", "방랑자·회절", "방랑자·인멸"]
    rover_idx = 0

    soup = fetch_soup(CHARACTER_LIST_URL)

    heading = _find_attribute_heading(soup)

    if heading is None:
        raise ValueError("[ 속성 ] 섹션을 찾을 수 없습니다.")

    character_urls = {}
    seen_hrefs = set()

    # ATTRIBUTE_NAMES로 "시작하는" tr을 찾는다 (실제 라벨은 "응결(Glacio |
    # 冷凝)"처럼 영문/한자가 붙어 있어 정확 일치 대신 접두어 일치로 확인).
    for el in heading.find_all_next():

        if el.name == "h2":
            break

        if el.name != "tr":
            continue

        label_text = el.get_text(strip=True)

        if not any(label_text.startswith(name) for name in ATTRIBUTE_NAMES):
            continue

        data_tr = el.find_next_sibling("tr")

        if data_tr is None:
            continue

        for link in data_tr.find_all("a"):

            href = link.get("href")

            if not href or not href.startswith("/w/") or href in seen_hrefs:
                continue

            seen_hrefs.add(href)

            name = link.get("title")

            if not name:
                strong = link.find("strong")
                name = strong.get_text(strip=True) if strong else None

            if not name:
                continue

            name = _DISAMBIGUATION_SUFFIX.sub("", name).strip()

            if not name:
                continue

            if name == "방랑자":
                name = rover_names[rover_idx]
                rover_idx += 1
            elif name.startswith("방랑자/"):
                # 실제 title은 "방랑자/전도"처럼 "/"로 붙어 나온다.
                # 표기를 다른 방랑자 변형과 동일하게 "·"로 통일한다.
                name = "방랑자·" + name[len("방랑자/"):]

            character_urls[name] = "https://namu.wiki" + href

    return character_urls


def crawl_weapon_stats(url: str) -> list[dict]:
    """무기 종류별 문서에서 무기명과 능력치 / 재련 정보를 수집해서 리스트로 반환한다."""
    soup = fetch_soup(url)

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
        texts = list(trs[1].stripped_strings)

        if len(texts) < 4:
            continue

        stat1_value, stat2_name, stat2_value = texts[1:4]
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

    return weapons


def save_json(data: list, path: str) -> None:
    """data를 UTF-8 JSON 파일로 저장한다. (ensure_ascii=False, indent=4)"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
