from pathlib import Path

from util import (
    crawl_character_urls,
    save,
    find_name,
    fetch_soup,
    find_attribute_section,
    extract_img_src,
    in_noscript,
    is_resonator_alt,
    resonator_name_from_alt,
    to_https,
)

seen = set()

THUMBNAIL_DIR = Path("resources/images/thumbnails")

THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

def find_thumbnail_url(wiki_url):
    soup = fetch_soup(wiki_url)

    # [ 속성별 ] 섹션 찾기
    attribute_section = find_attribute_section(soup)

    # 이미지 경로 가져오기
    for img in attribute_section.select('img[alt$="아이콘"]'):

        # noscript 내부 중복 제거
        if in_noscript(img):
            continue

        alt = img.get("alt", "")

        if not is_resonator_alt(alt):
            continue

        name = resonator_name_from_alt(alt)

        if name in seen:
            continue

        seen.add(name)

        src = extract_img_src(img)

        if not src:
            continue

        if src.startswith("//"):
            return to_https(src)


if __name__ == "__main__":
    character_urls = crawl_character_urls()

    for name in character_urls:

        wiki_url = character_urls.get(name)

        if wiki_url is None:
            print(f"[실패] {name}: 문서 URL 없음")
            continue

        try:
            src = find_thumbnail_url(wiki_url)
            name = find_name(wiki_url)

            save(src, f"{name}-thumbnail", THUMBNAIL_DIR)

        except Exception as e:
            print(f"[오류] {name}: {e}")
