import cv2
import numpy as np
import os
from config import get_PROCESSED_DIR, get_A, get_B, get_GAMMA, get_PREVIEW_DIR, get_MARGIN_TOP, get_MARGIN_BOTTOM, get_MARGIN_LEFT, get_MARGIN_RIGHT

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
    
    # マージンを取得（パーセント）
    margin_top_percent = min(50.0, get_MARGIN_TOP())  # 50%を超える場合は50%に制限
    margin_bottom_percent = min(50.0, get_MARGIN_BOTTOM())  # 50%を超える場合は50%に制限
    margin_left_percent = min(50.0, get_MARGIN_LEFT())  # 50%を超える場合は50%に制限
    margin_right_percent = min(50.0, get_MARGIN_RIGHT())  # 50%を超える場合は50%に制限
    
    # 画像サイズを取得
    height, width = original_image.shape[:2]
    
    # パーセントからピクセル数を計算
    # 上下のマージンは縦サイズに対するパーセント
    margin_top = int(height * margin_top_percent / 100.0)
    margin_bottom = int(height * margin_bottom_percent / 100.0)
    # 左右のマージンは横サイズに対するパーセント
    margin_left = int(width * margin_left_percent / 100.0)
    margin_right = int(width * margin_right_percent / 100.0)
    
    # マージン領域の境界を定義（元の画像サイズからマージン分だけ内側に入った領域）
    margin_area_left = margin_left
    margin_area_right = width - margin_right
    margin_area_top = margin_top
    margin_area_bottom = height - margin_bottom
    
    # トーンカーブを適用してコントラストを上げた画像を作成（輪郭検出用のみ）
    gamma_value = get_GAMMA()
    enhanced_image = apply_tone_curve(original_image, gamma_value)
    gray = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    
    # マージンの外側を黒で塗りつぶす
    # 上側のマージン外側
    binary[0:margin_area_top, :] = 0
    # 下側のマージン外側
    binary[margin_area_bottom:height, :] = 0
    # 左側のマージン外側
    binary[:, 0:margin_area_left] = 0
    # 右側のマージン外側
    binary[:, margin_area_right:width] = 0
    
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
    
    # 赤矩形（バウンディングボックスのユニオン）の上下の辺を取得
    if len(merged_boxes) > 0:
        merged_box = merged_boxes[0]
        red_top_y = merged_box[1]  # 赤矩形の上辺
        red_bottom_y = merged_box[3]  # 赤矩形の下辺
    else:
        # バウンディングボックスがない場合はマージン領域を使用
        red_top_y = margin_area_top
        red_bottom_y = margin_area_bottom
    
    # 緑矩形の上下の辺を赤矩形の上下の辺と同一ライン上に揃える
    y1 = red_top_y
    y2 = red_bottom_y
    crop_height = y2 - y1
    
    # 縦横比4:3（縦4横3）に合わせて幅を計算（width = height * 3 / 4）
    crop_width = crop_height * 3 // 4
    
    # マージン領域内に収まるように調整
    # 幅がマージン領域を超える場合は、マージン領域の幅を使用し、高さを再計算
    margin_area_width = margin_area_right - margin_area_left
    if crop_width > margin_area_width:
        crop_width = margin_area_width
        crop_height = crop_width * 4 // 3
        # 高さを調整したので、上下の位置を再計算（中央揃え）
        center_y = (red_top_y + red_bottom_y) // 2
        y1 = center_y - crop_height // 2
        y2 = y1 + crop_height
        # マージン領域内に収まるように調整
        if y1 < margin_area_top:
            y1 = margin_area_top
            y2 = y1 + crop_height
        if y2 > margin_area_bottom:
            y2 = margin_area_bottom
            y1 = y2 - crop_height
    
    # 中央揃えでx座標を計算
    center_x = (margin_area_left + margin_area_right) // 2
    x1 = center_x - crop_width // 2
    x2 = x1 + crop_width
    
    # マージン領域内に収まるように調整
    if x1 < margin_area_left:
        x1 = margin_area_left
        x2 = x1 + crop_width
    if x2 > margin_area_right:
        x2 = margin_area_right
        x1 = x2 - crop_width
    
    top_left = (x1, y1)
    bottom_right = (x2, y2)
    print(f"top_left:{top_left}")
    print(f"bottom_right:{bottom_right}")

    # テスト用：白黒画像に矩形を描画して保存
    # 白黒画像を3チャンネル（BGR）に変換
    binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    # 画像の横のピクセル数に対して1%の線幅を計算
    binary_width = binary_bgr.shape[1]
    line_width = max(1, int(binary_width * 0.01))  # 最小1ピクセルを確保
    
    # マージンラインを描画（マージン領域の境界）
    # 上側のマージンライン
    cv2.line(binary_bgr, (0, margin_area_top), (binary_width, margin_area_top), (64, 64, 64), line_width)
    # 下側のマージンライン
    cv2.line(binary_bgr, (0, margin_area_bottom), (binary_width, margin_area_bottom), (64, 64, 64), line_width)
    # 左側のマージンライン
    cv2.line(binary_bgr, (margin_area_left, 0), (margin_area_left, binary_bgr.shape[0]), (64, 64, 64), line_width)
    # 右側のマージンライン
    cv2.line(binary_bgr, (margin_area_right, 0), (margin_area_right, binary_bgr.shape[0]), (64, 64, 64), line_width)
    
    # バウンディングボックスのユニオンを赤矩形で描画
    if len(merged_boxes) > 0:
        merged_box = merged_boxes[0]
        cv2.rectangle(binary_bgr, (merged_box[0], merged_box[1]), (merged_box[2], merged_box[3]), (0, 0, 255), line_width)
    
    # 最終トリミング矩形を緑矩形で描画
    cv2.rectangle(binary_bgr, top_left, bottom_right, (0, 255, 0), line_width)
    
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
    
    estimated_height = red_top_y * get_A() + get_B()
    # 5刻みの整数に丸める
    estimated_height = round(estimated_height / 5) * 5
    return red_top_y, estimated_height, processed_file_path, preview_file_path, binary_preview_path
