import requests
from bs4 import BeautifulSoup
from pathlib import Path
from io import BytesIO
from PIL import Image

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

URL = (
    "https://namu.wiki/w/"
    "%EB%AA%85%EC%A1%B0:%20%EC%9B%8C%EB%8D%94%EB%A7%81%20%EC%9B%A8%EC%9D%B4%EB%B8%8C/%EB%8D%B0%EC%9D%B4%ED%84%B0%20%EC%8A%A4%ED%85%8C%EC%9D%B4%EC%85%98"
)

SAVE_DIR = Path("resources/images/echoes")
SAVE_DIR.mkdir(parents=True, exist_ok=True)


def parse_echoes():
    html = requests.get(URL, headers=HEADERS).text
    soup = BeautifulSoup(html, "html.parser")

    result = []
    seen = set()

    for details in soup.find_all("details"):
        for table in details.find_all("table"):
            trs = table.find_all("tr")

            for tr in trs[1::2]:  # 에코 리스트 행만
                for img in tr.select("img"):
                    name = img.get("alt", "").replace("명조 ", "").strip()

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

                    if not name or name in seen:
                        continue

                    seen.add(name)

                    image_url = img.get("data-src")
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url

                    result.append({
                        "name": name,
                        "image_url": image_url
                    })

    return result


def download_echo_image(name, image_url):
    response = requests.get(image_url, headers=HEADERS)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))

    save_path = SAVE_DIR / f"{name}.png"

    image.save(save_path, "PNG")

    print(f"[완료] {save_path}")


def main():
    echoes = parse_echoes()

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