import logging
import re
import time
import urllib.parse
from pathlib import Path

from util import (
    fetch_soup,
    in_noscript,
    extract_img_src,
    to_https,
    save,
)

# 로그 레벨은 필요에 따라 조정한다(예: 디버깅 시 logging.DEBUG).
LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL, format="%(message)s")
logger = logging.getLogger("echo_crawler")

NAMU_DOMAIN = "https://namu.wiki"

# 크롤링 대상 페이지(등급별 적 문서). 다른 등급 페이지가 추가되면 여기에만 URL을
# 넣으면 된다. 추출된 이미지는 등급 구분 없이 ENEMY_DIR 한 폴더에 모아 저장한다.
_ENEMY_DOC = NAMU_DOMAIN + "/w/%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EC%A0%81/"

TARGET_URLS = [
    _ENEMY_DOC + "%ED%95%B4%EC%9D%BC%EA%B8%89",  # 해일급
    _ENEMY_DOC + "%EB%85%B8%EB%8F%84%EA%B8%89",  # 노도급
    _ENEMY_DOC + "%EA%B1%B0%EB%9E%91%EA%B8%89",  # 거랑급
    _ENEMY_DOC + "%EA%B2%BD%ED%8C%8C%EA%B8%89",  # 경파급
]

# 수집 대상 <strong> 텍스트 패턴. "코드명-한글명" 형태(예: H91-타종 거북이,
# W93-악몽 · 헤카테, Z02-공명의 메아리 · 플뢰르 드 리스)인 에코 항목만 뽑는다.
NAME_PATTERN = re.compile(r"^[A-Za-z0-9]+-[가-힣].*$")

# 매칭은 위 패턴으로 하되, 실제 이름은 "코드명-" 접두사를 뗀 한글 이름만 쓴다.
# 예: W70-타종 거북이 -> 타종 거북이
_CODE_PREFIX = re.compile(r"^[A-Za-z0-9]+-(.+)$")


def clean_enemy_name(strong_text):
    """<strong> 텍스트에서 "코드명-" 접두사를 제거한 이름을 반환한다."""
    match = _CODE_PREFIX.match(strong_text)
    return match.group(1).strip() if match else strong_text.strip()

# 나무위키 과도 요청 차단을 피하기 위한 하위 페이지 요청 간 딜레이(초).
REQUEST_DELAY_SEC = 1.5

ENEMY_DIR = Path("resources/images/echoes")
ENEMY_DIR.mkdir(parents=True, exist_ok=True)


def _image_from_sibling_div(name_div):
    """이름 div의 바로 앞 형제 <div> 안 <table>에서 "명조 " 이미지를 찾는다.

    없거나(형제 div 자체가 없음) 그 안에 유효한 이미지가 없으면 None.
    """
    image_div = name_div.find_previous_sibling("div")
    if image_div is None:
        return None

    image_table = image_div.find("table")
    if image_table is None:
        return None

    for img in image_table.find_all("img"):

        if in_noscript(img):
            continue

        alt = img.get("alt") or ""
        if alt.startswith("명조 "):
            return img

    return None


def _portrait_via_preceding_table(strong):
    """형제 div가 없을 때의 폴백: strong보다 앞쪽에서 가장 가까운
    포트레이트 테이블(_portrait_img가 인정하는 테이블)의 이미지를 쓴다."""
    for table in strong.find_all_previous("table"):
        img = _portrait_img(table)
        if img is not None:
            return img

    return None


def find_image_via_sibling_div(strong):
    """이름 div의 앞 형제 div(이미지 div)에서 "명조 " 이미지를 찾는다.
    형제 div가 없으면 앞쪽 가장 가까운 포트레이트 테이블로 폴백한다."""
    name_table = strong.find_parent("table")
    if name_table is None:
        return None

    name_div = name_table.find_parent("div")
    if name_div is None:
        return None

    img = _image_from_sibling_div(name_div)
    if img is not None:
        return img

    return _portrait_via_preceding_table(strong)


def extract_from_main(soup, source_url):
    """메인 페이지: 패턴에 맞는 <strong> + 이름 div 앞 형제 div의 "명조 " 이미지.

    반환: {name, image_url, source_url} 딕셔너리 리스트.
    """
    results = []

    for strong in soup.find_all("strong"):

        text = strong.get_text(strip=True)

        # 조건 1: <strong> 텍스트가 "코드명-한글명" 패턴과 일치
        if not NAME_PATTERN.match(text):
            continue

        # 조건 2: 이름 div 바로 앞 형제 div의 <table> 안에
        #         alt가 "명조 "로 시작하는 <img>가 존재
        img = find_image_via_sibling_div(strong)
        if img is None:
            logger.warning(f"[스킵] 이미지 매칭 실패(명조 이미지 없음) - {text}")
            continue

        src = extract_img_src(img)
        if not src or src.startswith("data:image"):
            logger.warning(f"[스킵] 이미지 URL 없음(placeholder) - {text}")
            continue

        results.append({
            "name": clean_enemy_name(text),
            "image_url": to_https(src),
            "source_url": source_url,
        })

    return results


# 하위 페이지: 이미지는 "보스 정보"(h3) 섹션, 이름은 "에코"(h2) 섹션의
# <table>에 각각 따로 있다 (메인 페이지의 형제 div 구조와 다름).

IMG_ALT_PREFIX = "명조 "


def _heading_by_span_id(soup, tag_names, wanted):
    """<span id="..."> 값이 wanted인 제목 태그(<h2>/<h3>)를 반환한다."""
    for heading in soup.find_all(tag_names):
        span = heading.find("span", id=True)
        if span and span.get("id", "").strip() == wanted:
            return heading

    return None


def _section_tables(heading, stop_tags):
    """heading 이후 stop_tags(다음 동급 이상 제목)가 나오기 전까지의 <table>들."""
    tables = []

    for el in heading.find_all_next():
        if el.name in stop_tags:
            break
        if el.name == "table":
            tables.append(el)

    return tables


def _first_myeongjo_img(table):
    """<table> 안에서 alt가 "명조 "로 시작하는 첫 <img>. (noscript 중복 제외)"""
    for img in table.find_all("img"):
        if in_noscript(img):
            continue
        if (img.get("alt") or "").startswith(IMG_ALT_PREFIX):
            return img

    return None


def _strip_name(text):
    """비교용 정규화: 앞뒤 공백과 꼬리의 말줄임표/마침표 등을 제거한다."""
    return text.strip().rstrip(".…· ").strip()


def _portrait_img(table):
    """table이 보스 포트레이트 테이블이면 그 <img>를 반환한다 (img alt와 첫
    strong 텍스트가 일치하는지로 HP/저항/소나타 등 아이콘 테이블과 구분)."""
    img = _first_myeongjo_img(table)
    if img is None:
        return None

    alt_name = _strip_name((img.get("alt") or "")[len(IMG_ALT_PREFIX):])
    strong = table.find("strong")
    strong_text = _strip_name(strong.get_text(strip=True)) if strong else ""

    if len(alt_name) < 2 or not strong_text:
        return None

    # namu가 긴 alt를 "..."로 자르므로 앞부분 일치도 허용한다.
    if (strong_text == alt_name
            or strong_text.startswith(alt_name)
            or alt_name.startswith(strong_text)):
        return img

    return None


def find_subpage_image_url(soup):
    """"보스 정보" 섹션의 포트레이트 테이블 중 마지막 것의 이미지 URL."""
    heading = _heading_by_span_id(soup, ["h3"], "보스 정보")
    if heading is None:
        return None

    portrait_imgs = [
        img
        for table in _section_tables(heading, ("h2", "h3"))
        if (img := _portrait_img(table)) is not None
    ]

    if not portrait_imgs:
        return None

    src = extract_img_src(portrait_imgs[-1])
    if not src or src.startswith("data:image"):
        return None

    return to_https(src)


def find_subpage_names(soup):
    """"에코" 섹션의 <table>에서 패턴에 맞는 <strong>의 접두사 제거된 이름 목록."""
    heading = _heading_by_span_id(soup, ["h2"], "에코")
    if heading is None:
        return []

    names = []

    for table in _section_tables(heading, ("h2",)):
        for strong in table.find_all("strong"):
            text = strong.get_text(strip=True)
            if not NAME_PATTERN.match(text):
                continue
            name = clean_enemy_name(text)
            if name not in names:
                names.append(name)

    return names


def extract_from_subpage(soup, source_url):
    """하위 페이지: "에코" 섹션의 이름 × "보스 정보" 섹션의 이미지."""
    names = find_subpage_names(soup)
    if not names:
        logger.warning(f"[스킵] 이름 없음 또는 이미지 매칭 실패 - {source_url} (에코 섹션 없음)")
        return []

    image_url = find_subpage_image_url(soup)
    if image_url is None:
        for name in names:
            logger.warning(f"[스킵] 이름 없음 또는 이미지 매칭 실패 - {name}")
        return []

    return [
        {"name": name, "image_url": image_url, "source_url": source_url}
        for name in names
    ]


def find_subpage_urls(soup):
    """<h3> 안에서 개별 문서로 연결되는 하위 페이지의 절대 URL 목록.
    해시 class명은 배포마다 바뀌므로, href가 "/w/"로 시작하고 "#"이
    없는 링크만 문서 링크로 판별한다."""
    urls = []

    for h3 in soup.find_all("h3"):
        for a in h3.find_all("a", href=True):
            href = a["href"]

            if not href.startswith("/w/"):
                continue
            if "#" in href:
                continue

            urls.append(NAMU_DOMAIN + href)

    return urls


_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_filename(name):
    """파일명으로 쓸 수 없는 문자를 제거하고 앞뒤 공백/마침표를 정리한다."""
    cleaned = _INVALID_FILENAME_CHARS.sub("", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().strip(".")
    return cleaned or "unnamed"


def crawl_enemies():
    enemies = []
    seen_names = set()
    visited_urls = set()

    def collect(items):
        for item in items:
            if item["name"] in seen_names:
                continue
            seen_names.add(item["name"])
            enemies.append(item)

    for target_url in TARGET_URLS:

        if target_url in visited_urls:
            continue
        visited_urls.add(target_url)

        logger.info(f"[페이지 이동] {target_url} 크롤링 시작")

        try:
            main_soup = fetch_soup(target_url)
        except Exception as e:
            logger.error(f"[건너뜀] {target_url}: {e}")
            continue

        # 1단계: 메인 페이지 (형제 div 구조 규칙)
        collect(extract_from_main(main_soup, target_url))

        # 2단계: <h3> 안 S5ro1EF0 링크로 연결된 하위 페이지 (섹션 기반 규칙)
        for sub_url in find_subpage_urls(main_soup):

            if sub_url in visited_urls:
                continue
            visited_urls.add(sub_url)

            sub_label = urllib.parse.unquote(sub_url.rsplit("/", 1)[-1])
            logger.info(f"[하위 페이지] {sub_label} 페이지 진입")

            time.sleep(REQUEST_DELAY_SEC)

            try:
                sub_soup = fetch_soup(sub_url)
            except Exception as e:
                logger.error(f"[건너뜀] {sub_url}: {e}")
                continue

            collect(extract_from_subpage(sub_soup, sub_url))

        time.sleep(REQUEST_DELAY_SEC)

    return enemies


def main():
    enemies = crawl_enemies()

    logger.info(f"적 수: {len(enemies)}")

    success_count = 0
    failed_count = 0

    for enemy in enemies:
        name = enemy["name"]

        result = save(enemy["image_url"], sanitize_filename(name), ENEMY_DIR, verbose=False)

        if isinstance(result, Exception):
            failed_count += 1
            logger.error(f"[실패] {name} 이미지 다운로드 오류: {result}")
        else:
            success_count += 1
            logger.info(f"[저장 완료] {name}")

    logger.info(
        f"총 {len(enemies)}개 중 {success_count}개 저장 성공, {failed_count}개 스킵"
    )


if __name__ == "__main__":
    main()
