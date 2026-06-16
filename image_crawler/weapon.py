import requests
from bs4 import BeautifulSoup
from pathlib import Path
from io import BytesIO
from PIL import Image

URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EB%AC%B4%EA%B8%B0"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TARGET_SECTIONS = {
    "5성 목록",
    "4성 목록",
    "3성 이하 목록"
}

SAVE_DIR = Path("images/weapons")
SAVE_DIR.mkdir(parents=True, exist_ok=True)


def crawl_weapons():
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    weapons = []
    seen = set()

    for summary in soup.find_all("summary"):

        title = summary.get_text(strip=True)

        if not any(section in title for section in TARGET_SECTIONS):
            continue

        section = summary.find_parent("details")

        if section is None:
            continue

        for img in section.select('img[alt^="명조 "]'):

            src = img.get("data-src") or img.get("src")

            if not src:
                continue

            if src.startswith("data:image"):
                continue

            if src.startswith("//"):
                src = "https:" + src

            name = (
                img["alt"]
                .replace("명조 ", "")
                .strip()
            )
            

            if name in seen:
                continue

            seen.add(name)

            weapons.append({
                "name": name,
                "image_url": src
            })

    return weapons


def download_weapon_image(weapon):
    response = requests.get(
        weapon["image_url"],
        headers=HEADERS
    )
    response.raise_for_status()

    img = Image.open(BytesIO(response.content))

    save_path = SAVE_DIR / f'{weapon["name"]}.png'

    img.save(save_path, "PNG")

    print(f"[완료] {save_path}")


def main():
    weapons = crawl_weapons()

    print(f"무기 수: {len(weapons)}")

    for weapon in weapons:
        try:
            download_weapon_image(weapon)
        except Exception as e:
            print(f"[실패] {weapon['name']}: {e}")


if __name__ == "__main__":
    main()
