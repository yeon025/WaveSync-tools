import base64
import shutil
from pathlib import Path

# echoes 폴더는 읽기 전용으로만 사용한다(수정/삭제/이름 변경 금지).
ECHO_DIR = Path("resources/images/echoes")
NEW_ECHO_DIR = Path("resources/images/new_echoes")

# 이미지로 취급할 확장자. 이 외의 파일(.DS_Store, .gitkeep 등)은 무시한다.
IMAGE_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg", ".gif", ".bmp"}


def encode_name(echo_name):
    """원본 이름(한글 포함) -> Base64 URL-safe 인코딩.

    같은 echo_name은 항상 같은 결과를 내는 결정적 인코딩이며, +, /는 각각
    -, _로 치환되고 끝의 패딩(=)은 제거되어 파일명으로 바로 사용할 수 있다.
    """
    raw = echo_name.encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).decode("ascii")
    return encoded.rstrip("=")


def decode_name(encoded_name):
    """encode_name의 역함수. 인코딩된 파일명(확장자 제외) -> 원본 이름 복원.

    나중에 Storage에서 파일명만으로 원본 이름을 조회할 때 사용한다.
    """
    padding = "=" * (-len(encoded_name) % 4)
    raw = base64.urlsafe_b64decode(encoded_name + padding)
    return raw.decode("utf-8")


def get_sorted_image_files():
    """echoes 폴더의 이미지 파일을 파일명 오름차순으로 정렬해 반환한다."""
    return sorted(
        (
            file
            for file in ECHO_DIR.iterdir()
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
        ),
        key=lambda f: f.name,
    )


def encode_and_copy_images():
    """echoes의 각 이미지를 Base64(URL-safe)로 인코딩한 이름으로 new_echoes에 복사한다."""
    NEW_ECHO_DIR.mkdir(parents=True, exist_ok=True)

    mapping = []  # (원본 파일, 인코딩된 파일명)

    for image_file in get_sorted_image_files():
        encoded_stem = encode_name(image_file.stem)
        new_name = f"{encoded_stem}{image_file.suffix.lower()}"
        new_path = NEW_ECHO_DIR / new_name

        shutil.copy2(image_file, new_path)  # 원본은 그대로 두고 복사만 한다.

        mapping.append((image_file.name, new_name))

    return mapping


def main():
    mapping = encode_and_copy_images()

    print(f"총 {len(mapping)}개 이미지 처리 완료 -> {NEW_ECHO_DIR}")
    for original_name, encoded_name in mapping:
        print(f"{original_name} -> {encoded_name}")

    if mapping:
        sample_encoded = Path(mapping[0][1]).stem
        print(f"\n[검증] {sample_encoded} -> {decode_name(sample_encoded)}")


if __name__ == "__main__":
    main()
