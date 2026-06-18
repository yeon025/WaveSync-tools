import cv2
from src.profile.constant import IMAGE_PATH, RECTANGLES, CIRCLES




def run_masking(image_path: str):
    
    image = cv2.imread(image_path)


    # 직사각형 그리기
    for x1, y1, x2, y2 in RECTANGLES:
        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),  # 초록색
            1             # 선 두께
        )
        
    # 원 그리기
    for cx, cy, radius in CIRCLES:
        cv2.circle(
            image,
            (cx, cy),    # 중심 좌표
            radius,      # 반지름
            (255, 255, 0), # 시안
            2            # 선 두께
        )

    # 화면 표시용 축소
    DISPLAY_WIDTH = 1200

    h, w = image.shape[:2]
    scale = DISPLAY_WIDTH / w
    display_height = int(h * scale)

    display_image = cv2.resize(
        image,
        (DISPLAY_WIDTH, display_height)
    )

    # 출력
    cv2.imshow("Image", display_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()



if __name__ == "__main__":
    run_masking(IMAGE_PATH)