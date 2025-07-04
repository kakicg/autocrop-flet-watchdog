import flet as ft
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from image_processing import process_image
from item_db import ItemInfo, session
import time
from datetime import datetime

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
        current_mode = self.page.session.get('mode')
        
        # バーコードが変更された場合、アングル番号をリセット
        if barcode_number != self.last_barcode:
            self.current_angle = 0
            self.last_barcode = barcode_number
        
        if barcode_number:
            self.current_angle += 1
            new_name = f"{barcode_number}.jpg"
            # --- SideBarのmiddle_listsを更新 ---
            if hasattr(self.page, 'side_bar'):
                for container in self.page.side_bar.middle_lists:
                    if isinstance(container, ft.Container) and hasattr(container, 'content'):
                        content = container.content
                        if isinstance(content, ft.Text) and content.value == barcode_number:
                            container.bgcolor = "#028F68"
                            content.color = "white"
                            break
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
        
        # 現在のタイムスタンプを取得
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 新しい画像コンテナを作成
        image_container = ft.Container(
            content=ft.Column(
                [
                    ft.Image(
                        src=abs_processed_path,
                        fit=ft.ImageFit.CONTAIN,
                        repeat=ft.ImageRepeat.NO_REPEAT,
                        height=150
                    ),
                    ft.Text(
                        f"{new_name}",
                        size=12,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Text(
                        f"推定高さ:{estimated_height}",
                        style=text_style,
                        size=12,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_100,
                    ),
                    ft.Text(
                        f"[ {current_time} ]",
                        style=text_style,
                        size=10,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_100,
                    ),
                ],
                spacing=5,
            ),
            padding=10,
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=10,
            margin=5,
        )

        try:
            # メインビューのコントロールに追加
            if len(self.view_controls) > 1:
                self.view_controls[1].controls.insert(0, image_container)
            else:
                self.view_controls.insert(1, ft.ListView(
                    controls=[image_container],
                    horizontal=True,
                    height=320,
                ))

            # single_angleモードの場合、画像処理完了後にバーコード情報をクリア
            if current_mode == 'single_angle' and barcode_number:
                self.page.session.set('barcode_number', '')
                self.last_barcode = None
                self.current_angle = 0
                
                # メッセージを更新
                if len(self.view_controls) > 0:
                    top_container = self.view_controls[0]
                    if isinstance(top_container, ft.Container):
                        top_container.border = ft.border.all(6, ft.Colors.PINK_100)
                        if isinstance(top_container.content, ft.Text):
                            top_container.content.value = 'バーコードを読み取ってください'

            self.page.update()
        except Exception as e:
            print(f"Error updating UI: {e}")

def start_watchdog(page: ft.Page, view_controls, watch_folder="./watch_folder"):
    os.makedirs(watch_folder, exist_ok=True)
    event_handler = ImageHandler(page, view_controls)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    return observer 