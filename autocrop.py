import flet as ft
import time
from gui import start_gui, add_image_and_update
from camera import monitor_camera
from image_processing import process_image
import random

def main(page: ft.Page):
    start_gui(page)
    i=1
    while True:
        page.session.set("barcode_loop", True)
        page.controls[0].visible = True
        page.controls[1].visible = False
        page.update()
        while True: 
            """バーコードを読み取り、商品情報を取得する"""
            # バーコードを読み取る
            page.controls[0].controls[1].focus()
            time.sleep(1)
            if not page.session.get("barcode_loop"):
                item_str = "".join([str(random.randint(0, 9)) for _ in range(6)])
                break
        
        page.controls[0].visible = False
        page.controls[1].visible = True
        angle = 1
        page.session.set("gridview_loop", True)
        while page.session.get("gridview_loop"):
            #カメラ画像の監視
            page.session.set("camera_loop", True)
            # images = monitor_camera(page)
            process_image()
            # トリミングが画像の表示
            add_image_and_update(
                page, 
                f"https://picsum.photos/200/300?{i}", 
                item_str,
                random.randint(100, 999)
            )
            i += 1
            angle += 1
            time.sleep(1)
            

ft.app(main, view=ft.AppView.WEB_BROWSER)