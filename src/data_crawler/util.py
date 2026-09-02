"""data_crawler 공통 유틸리티.

base_stat / resonance_node / weapon 크롤러에서 반복적으로 쓰이는
상수, HTTP 요청/파싱, 공명자 문서 수집, 무기 능력치 파싱, JSON 저장 로직을 모아둔다.
"""

import json
import requests
from bs4 import BeautifulSoup


# =============================================================================
# 상수
# =============================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)


# =============================================================================
# HTTP / 파싱
# =============================================================================

def fetch_soup(url: str) -> BeautifulSoup:
    """URL을 GET 요청하고 응답 HTML을 BeautifulSoup 객체로 파싱해서 반환한다."""
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


# =============================================================================
# 공명자 문서 수집
# =============================================================================

def crawl_character_urls() -> dict[str, str]:
    """[ 속성별 ] 섹션에서 공명자 이름 -> 나무위키 문서 URL 딕셔너리를 만든다.

    "방랑자"는 등장 순서대로 전도 / 기류 / 회절 / 인멸로 구분한다.
    """
    rover_names = ["방랑자·전도", "방랑자·기류", "방랑자·회절", "방랑자·인멸"]
    rover_idx = 0

    soup = fetch_soup(CHARACTER_LIST_URL)

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
            name = rover_names[rover_idx]
            rover_idx += 1

        href = link.get("href")

        if not href:
            continue

        character_urls[name] = "https://namu.wiki" + href

    return character_urls


# =============================================================================
# 무기 능력치 파싱
# =============================================================================

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


# =============================================================================
# 저장
# =============================================================================

def save_json(data: list, path: str) -> None:
    """data를 UTF-8 JSON 파일로 저장한다. (ensure_ascii=False, indent=4)"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
