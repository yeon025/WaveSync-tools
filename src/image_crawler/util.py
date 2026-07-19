import requests
from bs4 import BeautifulSoup
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


def find_name(wiki_url):
    response = requests.get(wiki_url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    strong = soup.select_one("strong:has(ruby)")

    english_name = strong.get_text(" ", strip=True).split("|")[-1].strip()
    print(english_name)

    return english_name





def save(src, name, save_dir, type):
    save_dir.mkdir(exist_ok=True)

    characters = []

    try:
        image_response = requests.get(src, headers=HEADERS)
        image_response.raise_for_status()

        image = Image.open(BytesIO(image_response.content))

        file_path = save_dir / f"{name}-{type}.webp"

        image.save(file_path, "WEBP")

        characters.append({
            "name": name,
            "image_url": src,
            "file_path": str(file_path)
        })

        print(f"저장 완료: {file_path}")

    except Exception as e:
        print(f"{name} 저장 실패: {e}")