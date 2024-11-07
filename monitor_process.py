import flet as ft
import time
# from camera import get_camera_files_with_timestamps, download_file, delete_all_files
from gphoto2 import gp2
from image_processing import process_image
import os
from item_db import ItemInfo, session


text_style = ft.TextStyle(font_family="Noto Sans CJK JP")

def monitor_and_process(
        page:ft.Page, 
        view_controls,
        download_folder="./camera_images", 
        interval=0.5):
    gp2.delete_all_files()  # ループに入る前にカメラ内の全ファイルを削除
    """新しいファイルが見つかるまで監視し、見つかったら終了してファイルリストを返す"""
    os.makedirs(download_folder, exist_ok=True)  # 保存先フォルダを作成
    while page.session.get("camera_loop"):
        time.sleep(interval)
        new_files = gp2.get_camera_files_with_timestamps()
        # カメラ内に新しい画像を検出
        if new_files:
            # for file_number, file_name, timestamp in new_files:
            file_number, file_name, timestamp = new_files[-1]
            print(f"File: {file_name}, Timestamp: {timestamp}")
            gp2.download_file(file_number, file_name, download_folder)
            barcode_number = page.session.get('barcode_number')
            current_angle = page.session.get('current_angle')
            current_angle += 1
            page.session.set('current_angle', current_angle)
            new_name = f"{barcode_number}_{current_angle}.jpg"

            original = os.path.join(download_folder, file_name)
            estimated_height, processed_path = process_image(original , new_name)
            new_item = ItemInfo(
                    barcode=barcode_number,
                    precessed_url=processed_path,
                    original_url=original,
                    height=float(estimated_height)
                )
            session.add(new_item)
            session.commit()
            view_controls.insert(
                0,
                ft.Column(
                    [
                        ft.Text(
                            f"[ {new_name} ]",
                            size=12,
                            color=ft.colors.WHITE,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Text(
                            f"推定高さ:{estimated_height}",
                            style=text_style,
                            size=12,
                            color=ft.colors.WHITE,
                            weight=ft.FontWeight.W_100,
                        ),
                        ft.Image(
                            src=f"{processed_path}",
                            fit=ft.ImageFit.COVER,
                            repeat=ft.ImageRepeat.NO_REPEAT,
                        ),
                    ]
                ),
            )
            page.update()
            gp2.delete_all_files()  # ダウンロード後にカメラ内のファイルを削除
            
