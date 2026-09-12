from pathlib import Path

from util import (
    fetch_soup,
    in_noscript,
    is_resonator_alt,
    extract_img_src,
    to_https,
    save,
)

URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EB%AC%B4%EA%B8%B0"
)

TARGET_SECTIONS = {
    "5성 목록",
    "4성 목록",
    "3성 이하 목록"
}

WEAPON_DIR = Path("resources/images/weapons")
WEAPON_DIR.mkdir(parents=True, exist_ok=True)


def crawl_weapons():
    soup = fetch_soup(URL)

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
                if in_noscript(img):
                    continue

                alt = img.get("alt")
                if not is_resonator_alt(alt):
                    continue

                src = extract_img_src(img)

                if not src or src.startswith("data:image"):
                    continue

                src = to_https(src)

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


def main():
    weapons = crawl_weapons()

    print(f"무기 수: {len(weapons)}")

    for weapon in weapons:
        save(weapon["image_url"], weapon["name"], WEAPON_DIR)


if __name__ == "__main__":
    main()
