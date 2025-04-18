import cv2
import os

def process_image(image_path: str, barcode: str, mode: str, new_name: str = None, estimated_height: float = None) -> tuple:
    """画像処理を行う関数"""
    try:
        # 画像を読み込む
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"画像を読み込めません: {image_path}")

        # 画像のサイズを取得
        height, width = image.shape[:2]
        
        # 表示領域のサイズ（250x250）に合わせてリサイズ
        max_size = 250
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
            
        resized_image = cv2.resize(image, (new_width, new_height))
        
        # リサイズした画像を保存
        processed_path = os.path.join(PROCESSED_DIR, os.path.basename(image_path))
        cv2.imwrite(processed_path, resized_image)

        # データベースに保存
        save_to_db(processed_path, barcode, mode, new_name, estimated_height)

        return processed_path, barcode, mode, new_name, estimated_height

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return None, None, None, None, None 