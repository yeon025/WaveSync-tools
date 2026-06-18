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

SAVE_DIR = Path("resources/images/weapons")
SAVE_DIR.mkdir(parents=True, exist_ok=True)


def crawl_weapons():
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    weapons = []
    images = []
    names = []

    for details in soup.find_all("details"):

        summary = details.find("summary")
        if not summary:
            continue

        title = summary.get_text(strip=True)

        if not any(section in title for section in TARGET_SECTIONS):
            continue

        trs = details.find_all("tr")


        for tr in trs:
            # 이미지 추출    
            for img in tr.select("img"):
                # noscript 내부 중복 제거
                if img.find_parent("noscript"):
                    continue
                
                alt = img.get("alt")
                if not alt or not alt.startswith("명조 "):
                    continue

                src = img.get("data-src") or img.get("src")

                if not src or src.startswith("data:image"):
                    continue

                if src.startswith("//"):
                    src = "https:" + src

                images.append(src)

            # 이름 추출
            for a in tr.select("strong a"):
                name = a.get_text(strip=True)
                if name:
                    names.append(name)

            # 매칭
            if len(images) == len(names):
                for i, name in enumerate(names):
                    weapons.append({
                        "name": name,
                        "image_url": images[i]
                    })
                images = []
                names = []

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