from pathlib import Path

from util import (
    crawl_character_urls,
    save,
    find_name,
    fetch_soup,
    extract_img_src,
    in_noscript,
    is_resonator_alt,
    resonator_name_from_alt,
    to_https,
)

seen = set()

THUMBNAIL_DIR = Path("resources/images/thumbnails")

THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


def find_thumbnail_url(wiki_url, name):
    soup = fetch_soup(wiki_url)

    # 이미지 경로 가져오기
    for img in soup.select(f'img[alt="명조 {name} 아이콘"]'):

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
            src = find_thumbnail_url(wiki_url, name)
            english_name = find_name(wiki_url)

            save(src, f"{english_name}-thumbnail", THUMBNAIL_DIR)

        except Exception as e:
            print(f"[오류] {name}: {e}")
