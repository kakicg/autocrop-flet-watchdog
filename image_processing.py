import cv2
import numpy as np
import os
from config import get_PROCESSED_DIR, get_A, get_B

# (No changes here yet, just preparing for import of constants from config.py)

def process_image(original_image_path, filename, preview_name):
    # 元のファイル名を抽出
    
    image = cv2.imread(original_image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    dilated = cv2.dilate(opening, kernel, iterations=4)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = []
    for contour in contours:
        # 輪郭に外接する長方形（バウンディングボックス）を計算
        x, y, w, h = cv2.boundingRect(contour)
        bounding_boxes.append([x, y, x + w, y + h])

    # バウンディングボックス同士を結合する関数
    def merge_boxes(boxes):
        if len(boxes) == 0:
            return []

        # バウンディングボックスの最小と最大の座標を初期化
        x_min = min([box[0] for box in boxes])
        y_min = min([box[1] for box in boxes])
        x_max = max([box[2] for box in boxes])
        y_max = max([box[3] for box in boxes])

        return [[x_min, y_min, x_max, y_max]]

    # すべてのバウンディングボックスを結合
    merged_boxes = merge_boxes(bounding_boxes)
    # 結合されたバウンディングボックスを描画（赤色の矩形）
    # for box in merged_boxes:
    #     cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
    
    outerbox_height = image.shape[0]
    top_y = merged_boxes[0][1]
    if len(merged_boxes)>0:
        outerbox_height = outerbox_height - top_y
    print(f"outerbox_height:{outerbox_height}")
    top_margin = 80
    if top_y >= top_margin:
        outerbox_height += top_margin
    else:
        outerbox_height = image.shape[0]
    outerbox_width = outerbox_height * 9 // 16
    left = (image.shape[1] - outerbox_width)//2
    top = image.shape[0] - outerbox_height
    top_left = (left, top)
    print(f"top_left:{top_left}")

    bottom_right = (left + outerbox_width , image.shape[0])
    print(f"bottom_right:{bottom_right}")

    # top_left, bottom_right = (x1, y1), (x2, y2)
    x1, y1 = top_left
    x2, y2 = bottom_right

    # 画像をトリミング
    cropped_image = image[y1:y2, x1:x2]

    # 結果をファイルとして保存する
    processed_dir = get_PROCESSED_DIR()
    os.makedirs(processed_dir, exist_ok=True)  # 保存先フォルダを作成
    output_file_path = os.path.join(processed_dir, filename)
    cv2.imwrite(output_file_path, cropped_image)
    print(f"画像が '{output_file_path}' として保存されました。")
    
    # previewフォルダに同じ画像を保存
    preview_dir = "preview"
    os.makedirs(preview_dir, exist_ok=True)  # previewフォルダを作成（なければ作成）
    preview_file_path = os.path.join(preview_dir, preview_name)
    cv2.imwrite(preview_file_path, cropped_image)
    print(f"プレビュー画像が '{preview_file_path}' として保存されました。")
    
    estimated_height = top_y * get_A() + get_B()
    # 5刻みの整数に丸める
    estimated_height = round(estimated_height / 5) * 5
    return top_y, estimated_height, output_file_path, preview_file_path

