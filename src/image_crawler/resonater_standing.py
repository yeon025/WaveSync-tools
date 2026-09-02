from pathlib import Path

from util import (
    crawl_character_urls,
    save,
    find_name,
    fetch_soup,
    extract_img_src,
    to_https,
)


STANDING_DIR = Path("resources/images/standings")

STANDING_DIR.mkdir(parents=True, exist_ok=True)




def find_standing_image(section):
    """
    [ 스탠딩 ] 섹션 내부의 실제 이미지를 찾는다.
    placeholder(svg)는 제외한다.
    """

    for img in section.select("img"):
        src = extract_img_src(img)

        if not src:
            continue

        if src.startswith("data:image"):
            continue

        return img

    return None


def find_standing_url(wiki_url, name):

    soup = fetch_soup(wiki_url)

    summary = None

    for s in soup.find_all("summary"):
        title = s.get_text(strip=True)

        if "스탠딩" in title:
            summary = s
            break

    if summary is None:
        print(f"[실패] {name}: 스탠딩 섹션 없음")
        return

    standing_section = summary.find_parent("details")

    if standing_section is None:
        print(f"[실패] {name}: 스탠딩 details 없음")
        return

    image = find_standing_image(standing_section)

    if image is None:
        print(f"[실패] {name}: 이미지 없음")
        return

    src = extract_img_src(image)

    if src.startswith("//"):
        return to_https(src)



def main():

    character_urls = crawl_character_urls()

    for name in character_urls:

        wiki_url = character_urls.get(name)

        if wiki_url is None:
            print(f"[실패] {name}: 문서 URL 없음")
            continue

        try:
            src = find_standing_url(wiki_url, name)
            name = find_name(wiki_url)

            save(src, f"{name}-standing", STANDING_DIR)

        except Exception as e:
            print(f"[오류] {name}: {e}")


if __name__ == "__main__":
    main()
