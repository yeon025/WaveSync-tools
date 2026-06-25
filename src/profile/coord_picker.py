import cv2
from constant import IMAGE_PATH



drawing = False
x1, y1 = -1, -1

# 원본 이미지 로드
original_img = cv2.imread(IMAGE_PATH)

if original_img is None:
    raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {IMAGE_PATH}")

# 화면에 맞게 축소
height, width = original_img.shape[:2]

MAX_WIDTH = 1200
MAX_HEIGHT = 800

scale = min(
    MAX_WIDTH / width,
    MAX_HEIGHT / height,
    1.0  # 작은 이미지는 확대하지 않음
)

display_img = cv2.resize(
    original_img,
    (int(width * scale), int(height * scale))
)

img = display_img.copy()
original = display_img.copy()


def draw_rectangle(event, x, y, flags, param):
    global drawing, x1, y1, img, original

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x1, y1 = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            temp = img.copy()
            cv2.rectangle(temp, (x1, y1), (x, y), (0, 255, 0), 2)
            cv2.imshow("image", temp)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x2, y2 = x, y

        # 표시 이미지 기준 좌표
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)

        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.imshow("image", img)

        # 원본 이미지 기준 좌표로 변환
        original_x_min = int(x_min / scale)
        original_y_min = int(y_min / scale)
        original_x_max = int(x_max / scale)
        original_y_max = int(y_max / scale)

        print(
            f"원본 좌표: "
            f"({original_x_min}, {original_y_min}, "
            f"{original_x_max}, {original_y_max})"
        )


def run():
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", draw_rectangle)

    while True:
        cv2.imshow("image", img)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()