import cv2
from PIL import Image

def process_image(file_path, a, b):
    # 画像を読み込む
    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    
    # 輪郭を検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)
    
    # 最大矩形を取得
    x, y, w, h = cv2.boundingRect(max_contour)

    # 製品の高さを計算
    height = (img.shape[0] - y) * a + b

    # 画像をトリミング
    cropped_img = img[y:y+h, x:x+w]

    # PIL形式に変換
    cropped_img_pil = Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))

    return cropped_img_pil, height