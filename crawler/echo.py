import requests
from bs4 import BeautifulSoup
from pathlib import Path
from io import BytesIO
from PIL import Image

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

ECHO_URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EB%8D%B0%EC%9D%B4%ED%84%B0%20%EC%8A%A4%ED%85%8C%EC%9D%B4%EC%85%98"
)

SAVE_DIR = Path("images/echoes")
SAVE_DIR.mkdir(parents=True, exist_ok=True)


def get_echoes():
    response = requests.get(ECHO_URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    echoes = []
    seen = set()

    for img in soup.select("img._63CY-0Qw"):

        alt = img.get("alt", "")
        src = img.get("data-src") or img.get("src")
        filesize = int(img.get("data-filesize", 0))

        if not alt or not src:
            continue

        # 작은 아이콘 제외
        if filesize < 3000:
            continue

        name = (
            alt
            .replace("명조 ", "")
            .strip()
        )
        
        # 에코가 아닌 이미지 제외
        if (
            "명조로고" in name
            or "이벤트 아이콘" in name
            or "백팩" in name
        ):
            continue
            
        
        if "공명의 메아리 · 명식" in name:
            name = "공명의 메아리 · 명식 · 레비아탄"
        elif "공명의 메아리 · 악몽" in name:
            name = "공명의 메아리 · 악몽 아담 · 스매셔"
        elif "공명의 메아리 · 플뢰르" in name:
            name = "공명의 메아리 · 플뢰르 드 리스"
        elif "악몽 · 가시장미버섯(유" in name:
            name = "악몽 · 가시장미버섯(유체)"
        elif "악몽 · 그린멜팅카멜레온" in name:
            name = "악몽 · 그린멜팅카멜레온(유체)"
        elif "조각상을 재구성하는 돌멩" in name:
            name = "조각상을 재구성하는 돌멩이"
        elif "트윈 노바 · 네뷸러스" in name:
            name = "트윈 노바 · 네뷸러스 캐논"
        elif "트윈 노바 · 콜라사르" in name:
            name = "트윈 노바 · 콜라사르 블레이드"

        if name in seen:
            continue

        seen.add(name)

        if src.startswith("//"):
            src = "https:" + src

        echoes.append({
            "name": name,
            "image_url": src
        })

    return echoes


def download_echo_image(name, image_url):
    response = requests.get(image_url, headers=HEADERS)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))

    save_path = SAVE_DIR / f"{name}.png"

    image.save(save_path, "PNG")

    print(f"[완료] {save_path}")


def main():
    echoes = get_echoes()

    print(f"에코 수: {len(echoes)}")

    for echo in echoes:
        try:
            download_echo_image(
                echo["name"],
                echo["image_url"]
            )

        except Exception as e:
            print(f"[실패] {echo['name']}: {e}")


if __name__ == "__main__":
    main()