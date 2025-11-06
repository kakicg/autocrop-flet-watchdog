import cv2
import numpy as np
import os
from config import get_PROCESSED_DIR, get_A, get_B, get_GAMMA, get_PREVIEW_DIR

# (No changes here yet, just preparing for import of constants from config.py)

def apply_tone_curve(image, gamma=1.5):
    """
    トーンカーブを適用して中間値を下げ、コントラストを上げる
    
    Args:
        image: BGR形式の画像
        gamma: ガンマ値（大きいほど中間値が下がり、コントラストが上がる）
    
    Returns:
        処理済みのBGR画像
    """
    # 0-255の範囲でルックアップテーブルを作成
    lut = np.zeros((1, 256), dtype=np.uint8)
    for i in range(256):
        # ガンマ補正でコントラストを上げる
        # 中間値（128付近）を下げるように調整
        normalized = i / 255.0
        # S字カーブ風の調整で中間値を下げる
        adjusted = np.power(normalized, gamma) * 255.0
        # さらにコントラストを強調
        adjusted = np.clip(adjusted, 0, 255)
        lut[0, i] = int(adjusted)
    
    # 各チャンネルにLUTを適用
    result = cv2.LUT(image, lut)
    return result

def process_image(original_image_path, processed_file_path, preview_name):
    # 元のファイル名を抽出
    
    # オリジナル画像を読み込み（トリミング用に保持）
    original_image = cv2.imread(original_image_path)
    
    # トーンカーブを適用してコントラストを上げた画像を作成（輪郭検出用のみ）
    gamma_value = get_GAMMA()
    enhanced_image = apply_tone_curve(original_image, gamma_value)
    gray = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
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
    #     cv2.rectangle(enhanced_image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
    
    outerbox_height = original_image.shape[0]
    top_y = merged_boxes[0][1]
    if len(merged_boxes)>0:
        outerbox_height = outerbox_height - top_y
    print(f"outerbox_height:{outerbox_height}")
    top_margin = 80
    if top_y >= top_margin:
        outerbox_height += top_margin
    else:
        outerbox_height = original_image.shape[0]
    outerbox_width = outerbox_height * 3 // 4
    left = (original_image.shape[1] - outerbox_width)//2
    top = original_image.shape[0] - outerbox_height
    top_left = (left, top)
    print(f"top_left:{top_left}")

    bottom_right = (left + outerbox_width , original_image.shape[0])
    print(f"bottom_right:{bottom_right}")

    # top_left, bottom_right = (x1, y1), (x2, y2)
    x1, y1 = top_left
    x2, y2 = bottom_right

    # テスト用：白黒画像に矩形を描画して保存
    # 白黒画像を3チャンネル（BGR）に変換
    binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    # バウンディングボックスのユニオンを赤矩形で描画
    if len(merged_boxes) > 0:
        merged_box = merged_boxes[0]
        cv2.rectangle(binary_bgr, (merged_box[0], merged_box[1]), (merged_box[2], merged_box[3]), (0, 0, 255), 32)
    
    # 最終トリミング矩形を緑矩形で描画
    cv2.rectangle(binary_bgr, top_left, bottom_right, (0, 255, 0), 32)
    
    # previewフォルダーに保存
    preview_dir = get_PREVIEW_DIR()
    os.makedirs(preview_dir, exist_ok=True)
    # preview_nameから拡張子を除いてベース名を取得
    base_name = os.path.splitext(preview_name)[0]
    binary_preview_path = os.path.join(preview_dir, f"{base_name}_binary.jpg")
    cv2.imwrite(binary_preview_path, binary_bgr)
    print(f"白黒画像（テスト用）が '{binary_preview_path}' として保存されました。")

    # オリジナル画像からトリミング（コントラスト調整は適用しない）
    cropped_image = original_image[y1:y2, x1:x2]
    
    # 縦ピクセルサイズを1280にリサイズ（軽量化）
    height, width = cropped_image.shape[:2]
    if height > 1280:
        # アスペクト比を保持してリサイズ
        new_width = int(width * 1280 / height)
        cropped_image = cv2.resize(cropped_image, (new_width, 1280), interpolation=cv2.INTER_AREA)

    # 結果をファイルとして保存する
    cv2.imwrite(processed_file_path, cropped_image)
    print(f"画像が '{processed_file_path}' として保存されました。")
    
    # previewフォルダに同じ画像を保存
    preview_dir = get_PREVIEW_DIR()
    os.makedirs(preview_dir, exist_ok=True)  # previewフォルダを作成（なければ作成）
    preview_file_path = os.path.join(preview_dir, preview_name)
    cv2.imwrite(preview_file_path, cropped_image)
    print(f"プレビュー画像が '{preview_file_path}' として保存されました。")
    
    estimated_height = top_y * get_A() + get_B()
    # 5刻みの整数に丸める
    estimated_height = round(estimated_height / 5) * 5
    return top_y, estimated_height, processed_file_path, preview_file_path, binary_preview_path

