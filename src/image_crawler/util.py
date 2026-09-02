"""image_crawler 공통 유틸리티.

resonater_thumbnail / resonater_standing / weapon 크롤러에서 반복적으로
쓰이는 상수, HTTP 요청/파싱, HTML 요소 헬퍼, 이미지 다운로드/저장 로직을 모아둔다.
"""

import requests
from bs4 import BeautifulSoup, Tag
from pathlib import Path
from io import BytesIO
from PIL import Image


# =============================================================================
# 상수
# =============================================================================

CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# =============================================================================
# HTTP / 파싱
# =============================================================================

def fetch_soup(url: str) -> BeautifulSoup:
    """URL을 GET 요청하고 응답 HTML을 BeautifulSoup 객체로 파싱해서 반환한다."""
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


def find_attribute_section(soup: BeautifulSoup) -> Tag:
    """[ 속성별 ] 섹션을 감싸는 <details> 요소를 반환한다.

    섹션을 찾지 못하면 ValueError를 발생시킨다.
    """
    summary = soup.find(
        "summary",
        string=lambda s: s and "속성별" in s
    )

    if summary is None:
        raise ValueError("[ 속성별 ] 섹션을 찾을 수 없습니다.")

    return summary.find_parent("details")


# =============================================================================
# HTML 요소 헬퍼
# =============================================================================

def in_noscript(tag: Tag) -> bool:
    """태그가 <noscript> 내부에 있는지 여부. (스크립트 비활성화용 중복 이미지 판별)"""
    return tag.find_parent("noscript") is not None


def extract_img_src(img: Tag) -> str | None:
    """<img> 태그에서 실제 이미지 경로를 얻는다. (지연 로딩용 data-src 우선)"""
    return img.get("data-src") or img.get("src")


def to_https(src: str) -> str:
    """`//`로 시작하는 프로토콜 상대 URL 앞에 `https:` 스킴을 붙인다."""
    if src.startswith("//"):
        return "https:" + src

    return src


def is_resonator_alt(alt: str | None) -> bool:
    """alt 텍스트가 공명자 아이콘("명조 ...")을 가리키는지 여부."""
    return bool(alt) and alt.startswith("명조 ")


def resonator_name_from_alt(alt: str) -> str:
    """이미지 alt 텍스트에서 공명자 이름을 추출한다. 예) "명조 안코 아이콘" -> "안코"."""
    return alt.replace("명조 ", "").replace(" 아이콘", "")


# =============================================================================
# 공명자 문서 크롤링
# =============================================================================

def crawl_character_urls() -> dict[str, str]:
    """[ 속성별 ] 섹션에서 공명자 이름 -> 나무위키 문서 URL 딕셔너리를 만든다."""
    soup = fetch_soup(CHARACTER_LIST_URL)

    attribute_section = find_attribute_section(soup)

    character_urls: dict[str, str] = {}

    for link in attribute_section.select("a[href^='/w/']"):

        img = link.select_one("img[alt$='아이콘']")

        if img is None:
            continue

        if in_noscript(img):
            continue

        name = resonator_name_from_alt(img["alt"])

        href = link.get("href")

        if not href:
            continue

        character_urls[name] = "https://namu.wiki" + href

    return character_urls


def find_name(wiki_url: str) -> str:
    """공명자 문서에서 영문 이름을 추출해서 반환한다."""
    soup = fetch_soup(wiki_url)

    strong = soup.select_one("strong:has(ruby)")

    english_name = strong.get_text(" ", strip=True).split("|")[-1].strip()

    return english_name


# =============================================================================
# 이미지 다운로드 / 저장
# =============================================================================

def save(src: str, name: str, save_dir: Path) -> None:
    """이미지 URL을 내려받아 `{name}.webp`로 save_dir에 저장한다."""
    save_dir.mkdir(exist_ok=True)

    try:
        image_response = requests.get(src, headers=HEADERS)
        image_response.raise_for_status()

        image = Image.open(BytesIO(image_response.content))

        save_path = save_dir / f"{name}.webp"

        image.save(save_path, "WEBP")

        print(f"저장 완료: {save_path}")

    except Exception as e:
        print(f"{name} 저장 실패: {e}")
