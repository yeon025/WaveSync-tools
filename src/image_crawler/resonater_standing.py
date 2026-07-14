import requests
from bs4 import BeautifulSoup
from pathlib import Path
from io import BytesIO
from PIL import Image
from PIL import Image
from util import get_character_urls, save, find_name

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)


STANDING_DIR = Path("resources/images/standings")

STANDING_DIR.mkdir(parents=True, exist_ok=True)





def find_standing_image(section):
    """
    [ 스탠딩 ] 섹션 내부의 실제 이미지를 찾는다.
    placeholder(svg)는 제외한다.
    """

    for img in section.select("img"):
        src = img.get("data-src") or img.get("src")

        if not src:
            continue

        if src.startswith("data:image"):
            continue

        return img

    return None


def make_standing_path(name, wiki_url):

    response = requests.get(wiki_url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    summary = None

    for s in soup.find_all("summary"):
        text = s.get_text(strip=True)

        if "스탠딩" in text:
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

    src = image.get("data-src") or image.get("src")

    if src.startswith("//"):
        src = "https:" + src
        return src


def main():

    character_urls = get_character_urls()

    for name, url in character_urls.items():

        wiki_url = character_urls.get(name)

        if wiki_url is None:
            print(f"[실패] {name}: 문서 URL 없음")
            continue

        try:
            src = make_standing_path(name, wiki_url)
            name = find_name(wiki_url)

            save_dir = Path("resources/images/standings")
            save(src, name, save_dir, "standing")

        except Exception as e:
            print(f"[오류] {name}: {e}")


if __name__ == "__main__":
    main()