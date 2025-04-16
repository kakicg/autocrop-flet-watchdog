import flet as ft
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from image_processing import process_image
from item_db import ItemInfo, session
import time

text_style = ft.TextStyle(font_family="Noto Sans CJK JP")

class ImageHandler(FileSystemEventHandler):
    def __init__(self, page, view_controls):
        self.page = page
        self.view_controls = view_controls
        self.processed_files = set()
        self.current_angle = 0
        self.last_barcode = None

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            time.sleep(0.5)  # ファイルの書き込み完了を待つ
            self.process_image(event.src_path)

    def process_image(self, image_path):
        if image_path in self.processed_files:
            return
        
        self.processed_files.add(image_path)
        barcode_number = self.page.session.get('barcode_number')
        
        # バーコードが変更された場合、アングル番号をリセット
        if barcode_number != self.last_barcode:
            self.current_angle = 0
            self.last_barcode = barcode_number
        
        if barcode_number:
            self.current_angle += 1
            new_name = f"{barcode_number}_{self.current_angle}.jpg"
        else:
            new_name = os.path.basename(image_path)

        estimated_height, processed_path = process_image(image_path, new_name)
        
        new_item = ItemInfo(
            barcode=barcode_number if barcode_number else "unknown",
            precessed_url=processed_path,
            original_url=image_path,
            height=float(estimated_height)
        )
        session.add(new_item)
        session.commit()

        # 画像の絶対パスを取得
        abs_processed_path = os.path.abspath(processed_path)
        
        # 新しい画像コンテナを作成
        image_container = ft.Container(
            content=ft.Column(
                [
                    ft.Image(
                        src=abs_processed_path,
                        fit=ft.ImageFit.COVER,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        height=240
                    ),
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
                ],
                spacing=5,
            ),
            padding=10,
            bgcolor=ft.colors.BLUE_GREY_900,
            border_radius=10,
            margin=5,
        )

        # メインビューのコントロールに追加
        if len(self.view_controls) > 1:
            self.view_controls[1].controls.insert(0, image_container)
        else:
            self.view_controls.insert(1, ft.ListView(
                controls=[image_container],
                horizontal=True,
                height=320,
            ))

        self.page.update()

def start_watchdog(page: ft.Page, view_controls, watch_folder="./watch_folder"):
    os.makedirs(watch_folder, exist_ok=True)
    event_handler = ImageHandler(page, view_controls)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    return observer 