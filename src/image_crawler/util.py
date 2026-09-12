"""image_crawler 공통 유틸리티.

resonater_thumbnail / resonater_standing / weapon 크롤러에서 반복적으로
쓰이는 상수, HTTP 요청/파싱, HTML 요소 헬퍼, 이미지 다운로드/저장 로직을 모아둔다.
"""

import requests
from bs4 import BeautifulSoup, Tag
from pathlib import Path
from io import BytesIO
from PIL import Image


CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# "속성" 섹션에서 class="TrbsItZY" 카드로 찾은 링크 수가 이 값보다 적으면
# (namu.wiki의 해시 class명은 배포마다 바뀌므로) class 매칭이 깨졌다고 보고
# href="/w/..." 단독 매칭으로 폴백한다. 현재 공명자 수(40여 명)보다 훨씬
# 낮게 잡은 안전 마진이다.
MIN_ATTRIBUTE_LINKS = 20


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


def _find_attribute_heading(soup: BeautifulSoup) -> Tag | None:
    """"3. 속성" 섹션의 <h2> 헤딩을 찾는다 (섹션 번호는 하드코딩하지 않고
    id="속성" span, 없으면 id="s-3" 앵커로 폴백). 못 찾으면 None.

    find_attribute_section()과 별개다 — 그쪽은 resonater_thumbnail.py가
    여전히 쓰는 옛 [ 속성별 ] 구조 탐색이라 건드리지 않는다.
    """
    for heading in soup.find_all("h2"):
        if heading.find("span", id="속성"):
            return heading

        if heading.find("a", id="s-3"):
            return heading

    return None


def _resonator_links_in_section(heading: Tag) -> list[Tag]:
    """heading 다음 <h2> 전까지 href="/w/..."인 <a>를 모은다. class="TrbsItZY"
    카드를 우선하되, 해시 class명이 바뀌어 MIN_ATTRIBUTE_LINKS보다 적게
    잡히면 class 조건 없이 href만으로 다시 모은 목록으로 폴백한다."""
    links = []

    for el in heading.find_all_next():
        if el.name == "h2":
            break

        if el.name == "a" and (el.get("href") or "").startswith("/w/"):
            links.append(el)

    primary = [link for link in links if "TrbsItZY" in (link.get("class") or [])]

    if len(primary) >= MIN_ATTRIBUTE_LINKS:
        return primary

    return links


def crawl_character_urls() -> dict[str, str]:
    """"3. 속성" 섹션에서 공명자 이름 -> 나무위키 문서 URL 딕셔너리를 만든다."""
    soup = fetch_soup(CHARACTER_LIST_URL)

    heading = _find_attribute_heading(soup)

    if heading is None:
        raise ValueError("[ 속성 ] 섹션을 찾을 수 없습니다.")

    character_urls: dict[str, str] = {}
    seen_hrefs = set()

    for link in _resonator_links_in_section(heading):

        href = link.get("href")

        if not href or href in seen_hrefs:
            continue

        seen_hrefs.add(href)

        name = link.get("title")

        if not name:
            strong = link.find("strong")
            name = strong.get_text(strip=True) if strong else None

        if not name:
            continue

        character_urls[name] = "https://namu.wiki" + href

    return character_urls


def find_name(wiki_url: str) -> str:
    """공명자 문서에서 영문 이름을 추출해서 반환한다."""
    soup = fetch_soup(wiki_url)

    strong = soup.select_one("strong:has(ruby)")

    english_name = strong.get_text(" ", strip=True).split("|")[-1].strip()

    return english_name


def save(src: str, name: str, save_dir: Path, verbose: bool = True) -> Path | Exception:
    """이미지 URL을 내려받아 `{name}.webp`로 save_dir에 저장한다. 성공 시
    저장된 Path, 실패 시 예외 객체를 반환한다. verbose=False면 자체 print를
    생략한다(호출부가 따로 로깅할 때 중복 출력 방지용)."""
    save_dir.mkdir(exist_ok=True)

    save_path = save_dir / f"{name}.webp"

    try:
        image_response = requests.get(src, headers=HEADERS)
        image_response.raise_for_status()

        image = Image.open(BytesIO(image_response.content))

        image.save(save_path, "WEBP")

        if verbose:
            print(f"저장 완료: {save_path}")

        return save_path

    except Exception as e:
        if verbose:
            print(f"{name} 저장 실패: {e}")

        return e
