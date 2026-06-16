import requests
from bs4 import BeautifulSoup
from pathlib import Path
from io import BytesIO
from PIL import Image

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CHARACTER_LIST_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"
)

THUMBNAIL_DIR = Path("images/thumbnails")
STANDING_DIR = Path("images/standings")

STANDING_DIR.mkdir(parents=True, exist_ok=True)


def get_character_names():
    names = []

    for file in THUMBNAIL_DIR.glob("*-thumbnail.png"):
        name = file.stem.replace("-thumbnail", "")
        names.append(name)

    return names


def get_character_urls():
    response = requests.get(CHARACTER_LIST_URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

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

        href = link.get("href")

        if not href:
            continue

        character_urls[name] = "https://namu.wiki" + href

    return character_urls


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


def download_standing_image(name, wiki_url):
    print(f"처리 중: {name}")

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

    img_response = requests.get(src, headers=HEADERS)
    img_response.raise_for_status()

    img = Image.open(BytesIO(img_response.content))

    save_path = STANDING_DIR / f"{name}-standing.png"

    img.save(save_path, "PNG")

    print(f"[완료] {save_path}")


def main():
    names = get_character_names()

    if not names:
        print("썸네일 파일을 찾을 수 없습니다.")
        return

    character_urls = get_character_urls()

    print(f"썸네일 기준 캐릭터 수: {len(names)}")

    for name in names:

        wiki_url = character_urls.get(name)

        if wiki_url is None:
            print(f"[실패] {name}: 문서 URL 없음")
            continue

        try:
            download_standing_image(name, wiki_url)

        except Exception as e:
            print(f"[오류] {name}: {e}")


if __name__ == "__main__":
    main()