import flet as ft
import time
from gui import start_gui, add_image_and_update
from camera import monitor_camera
from image_processing import process_image
import threading
import http.server
import socketserver
import os

# HTTPサーバーの設定
PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

# グローバル
camera_images_folder = "./camera_images"
processed_images_foler = "./processed_images"

def start_http_server():
    """HTTPサーバーを起動する関数"""
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

def main(page: ft.Page):
    start_gui(page)
    i=1
    while True:
        page.session.set("barcode_loop", True)
        page.controls[0].visible = True #top1_rpw
        page.controls[1].visible = False #top2_rpw
        page.update()
        while True: 
            """バーコードを読み取り、商品情報を取得する"""
            # バーコードを読み取る
            page.controls[0].controls[1].focus() #barcode_textfield
            time.sleep(1)
            if not page.session.get("barcode_loop"):
                barcode_number = page.session.get("barcode_number")
                break
        
        page.controls[0].visible = False #top1_rpw
        page.controls[1].visible = True #top2_rpw
        page.update()
        angle = 1
        page.session.set("gridview_loop", True)
        while page.session.get("gridview_loop"):
            #カメラ画像の監視
            page.session.set("camera_loop", True)
            camera_file = monitor_camera(page)
            if not camera_file:
                break
            filename = f"{barcode_number}_{angle}.jpg"
            camera_path = os.path.join(camera_images_folder, camera_file)
            estimated_height, output_file_path = process_image(camera_path, filename)
            # トリミングが画像の表示
            print(f"output_file_path: {output_file_path}")
            add_image_and_update(
                page, 
                output_file_path, 
                barcode_number,
                estimated_height
            )
            i += 1
            angle += 1
            time.sleep(.1)
            
if __name__ == "__main__":
    # HTTPサーバーをバックグラウンドスレッドで起動
    # server_thread = threading.Thread(target=start_http_server, daemon=True)
    # server_thread.start()
    # ft.app(main, view=ft.AppView.WEB_BROWSER)
    ft.app(main)