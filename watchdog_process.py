import flet as ft
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from image_processing import process_image
from item_db import ItemInfo, session
import time
from datetime import datetime
from config import PROCESSED_DIR, WATCH_DIR, get_A, get_B, set_A_B

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
        current_mode = self.page.session.get('mode')
        barcode_number = self.page.session.get('barcode_number')
        if barcode_number:
            new_name = f"{barcode_number}.jpg"
            # --- SideBarのmiddle_listsを更新 ---
            if hasattr(self.page, 'side_bar'):
                for container in self.page.side_bar.middle_lists:
                    if isinstance(container, ft.Container) and hasattr(container, 'content'):
                        content = container.content
                        if isinstance(content, ft.Text) and content.value == barcode_number:
                            container.bgcolor = "#3DBCE2"
                            content.color = "white"
                            break
        else:
            new_name = os.path.basename(image_path)

        
        real_height = self.page.session.get('real_height')

    
        top_y, processed_path = process_image(image_path, new_name)


        
        estimated_height = top_y * get_A() + get_B()
        
        new_item = ItemInfo(
            barcode=barcode_number if barcode_number else "unknown",
            precessed_url=processed_path,
            original_url=image_path,
            height=float(estimated_height),
            top_y=int(top_y) if top_y is not None else None,
            real_height=int(real_height) if real_height is not None else None
        )
        session.add(new_item)
        session.commit()

        if real_height:
            # 直近のtop_y, real_heightペアを2つ取得
            recent_items = session.query(ItemInfo).filter(ItemInfo.top_y != None, ItemInfo.real_height != None).order_by(ItemInfo.id.desc()).limit(2).all()
            if len(recent_items) == 2:
                ty1, rh1 = recent_items[0].top_y, recent_items[0].real_height
                ty2, rh2 = recent_items[1].top_y, recent_items[1].real_height
                # 連立方程式を解く
                if ty1 != ty2:
                    a = (rh1 - rh2) / (ty1 - ty2)
                    b = rh1 - a * ty1
                    set_A_B(a, b)
            self.page.session.set("real_height", None)

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

            if barcode_number:
                self.page.session.set('barcode_number', '')
                self.last_barcode = None
                self.current_angle = 0

            self.page.update()
        except Exception as e:
            print(f"Error updating UI: {e}")

def start_watchdog(page: ft.Page, view_controls):
    os.makedirs(WATCH_DIR, exist_ok=True)
    event_handler = ImageHandler(page, view_controls)
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    return observer 