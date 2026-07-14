import requests
from bs4 import BeautifulSoup
from pathlib import Path
from util import get_character_urls, save, find_name

URL = "https://namu.wiki/w/%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"

CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

seen = set()


def find_thumbnail_image(name, wiki_url):
    response = requests.get(wiki_url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # [ 속성별 ] 섹션 찾기
    summary = soup.find(
        "summary",
        string=lambda s: s and "속성별" in s
    )

    if summary is None:
        raise ValueError("[ 속성별 ] 섹션을 찾을 수 없습니다.")

    attribute_section = summary.find_parent("details")

    save_dir = Path("resources/images/thumbnails")
    save_dir.mkdir(exist_ok=True)

    # 이미지 경로 가져오기
    for img in attribute_section.select('img[alt$="아이콘"]'):

        # noscript 내부 중복 제거
        if img.find_parent("noscript"):
            continue

        alt = img.get("alt", "")

        if not alt.startswith("명조 "):
            continue

        name = (alt.replace("명조 ", "").replace(" 아이콘", ""))

        if name in seen:
            continue

        seen.add(name)

        src = img.get("data-src") or img.get("src")

        if not src:
            continue

        if src.startswith("//"):
            src = "https:" + src
            return src


if __name__ == "__main__":
    character_urls = get_character_urls()

    for name, url in character_urls.items():

        wiki_url = character_urls.get(name)

        if wiki_url is None:
            print(f"[실패] {name}: 문서 URL 없음")
            continue

        try:
            src = find_thumbnail_image(name, wiki_url)
            name = find_name(wiki_url)

            save_dir = Path("resources/images/thumbnails")
            save(src, name, save_dir, "thumbnail")

        except Exception as e:
            print(f"[오류] {name}: {e}")