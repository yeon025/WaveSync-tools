import requests
from bs4 import BeautifulSoup, Tag
from pathlib import Path
from io import BytesIO
from PIL import Image
import re

CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)

HEADERS = {"User-Agent": "Mozilla/5.0"}

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
    """ "3. 속성" 섹션의 <h2> 헤딩을 찾는다 (섹션 번호는 하드코딩하지 않고
    id="속성" span, 없으면 id="s-3" 앵커로 폴백). 못 찾으면 None."""
    for heading in soup.find_all("h2"):
        if heading.find("span", id="속성"):
            return heading

        if heading.find("a", id="s-3"):
            return heading

    return None


def crawl_character_urls() -> dict[str, str]:
    """ "3. 속성" 섹션 아래 속성별 표(이름 tr 다음 형제 tr에 링크)에서 공명자
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
                name = "방랑자·" + name[len("방랑자/") :]

            character_urls[name] = "https://namu.wiki" + href

    return character_urls


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
