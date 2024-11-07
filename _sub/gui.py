import flet as ft
global barcode_textfield_ref
import os
import socket

PORT = 8000
local_ip = "192.168.2.194"
text_style = ft.TextStyle(font_family="Noto Sans CJK JP")

def start_gui(page: ft.Page):
    def set_item(event):
        page.session.set("barcode_number", event.control.value)
        event.control.value = ""
        page.session.set("barcode_loop", False)
        page.update()

    def next_item(event):
        page.session.set("gridview_loop", False)
        page.session.set("camera_loop", False)
        # page
        
    barcode_textfield = ft.TextField(on_submit=set_item, border_color=ft.colors.BLACK)
    barcode_controls = [
        ft.Text("バーコードをスキャンしてください", style=text_style, size=12, color=ft.colors.WHITE),
        barcode_textfield
    ]
    top1_row = ft.Row(barcode_controls)
    page.add(top1_row)

    item_infos = [
        ft.Text("商品情報", style=text_style, size=12, color=ft.colors.WHITE, weight=ft.FontWeight.W_600),
        ft.FilledTonalButton(
            content=ft.Text("次へ", style=text_style),
            on_click=next_item,
        ),
    ]
    top2_row = ft.Row(item_infos)
    page.add(top2_row)

    gridview = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=200,
        child_aspect_ratio=0.5625,
        spacing=30,
        run_spacing=10,
    )
    page.add(gridview)

def add_image_and_update(page: ft.Page, image_path: str, item_num: str, height: float):
    """FletのGUIを更新して画像と高さ情報を表示する"""
    global PORT
    # hostname = socket.gethostname()
    # local_ip = socket.gethostbyname(hostname)
    # 画像コンポーネントの作成
    gridview = page.controls[-1]
    image_absolute_path = os.path.abspath(image_path)
    print(f"絶対パス：{image_absolute_path}")
    
    imgpath = f"http://192.168.2.194:8000{image_path[1:]}"
    print(imgpath)

    gridview.controls.insert(0,
        ft.Column(
            [
                ft.Text(
                    f"[ {item_num} ]",
                    size=12,
                    color=ft.colors.WHITE,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Text(
                    f"推定高さ:{height}",
                    style=text_style,
                    size=12,
                    color=ft.colors.WHITE,
                    weight=ft.FontWeight.W_100,
                ),
                ft.Image(
                    src=f"{image_absolute_path}",
                    # src=f"{imgpath}",
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                ),
            ]
        )            
    )
    page.update()
