import requests
from bs4 import BeautifulSoup
from pathlib import Path
from io import BytesIO
from PIL import Image

URL = "https://namu.wiki/w/%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EA%B3%B5%EB%AA%85%EC%9E%90"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def download_character_thumbnails():
    response = requests.get(URL, headers=HEADERS)
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

    save_dir = Path("images/thumbnails")
    save_dir.mkdir(exist_ok=True)

    characters = []
    seen = set()

    for img in attribute_section.select('img[alt$="아이콘"]'):

        # noscript 내부 중복 제거
        if img.find_parent("noscript"):
            continue

        alt = img.get("alt", "")

        if not alt.startswith("명조 "):
            continue

        name = (
            alt.replace("명조 ", "")
               .replace(" 아이콘", "")
        )

        if name in seen:
            continue

        seen.add(name)

        src = img.get("data-src") or img.get("src")

        if not src:
            continue

        if src.startswith("//"):
            src = "https:" + src

        try:
            image_response = requests.get(src, headers=HEADERS)
            image_response.raise_for_status()

            image = Image.open(BytesIO(image_response.content))

            file_path = save_dir / f"{name}-thumbnail.png"

            image.save(file_path, "PNG")

            characters.append({
                "name": name,
                "image_url": src,
                "file_path": str(file_path)
            })

            print(f"저장 완료: {file_path}")

        except Exception as e:
            print(f"{name} 저장 실패: {e}")

    print(f"\n총 {len(characters)}개 다운로드 완료")
    return characters


if __name__ == "__main__":
    download_character_thumbnails()