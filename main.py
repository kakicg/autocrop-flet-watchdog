import flet as ft
from sidebar import SideBar
from watchdog_process import start_watchdog
import optparse
import os

def main(page: ft.Page):
    def terminate(event):
        page.session.set("camera_loop", False)
        if hasattr(page, 'observer'):
            page.observer.stop()
            page.observer.join()
        page.window.close()

    def change_mode(event):
        print(f"change_mode: {page.session.get('mode')}")
        current_mode = page.session.get("mode")

        if current_mode is None or current_mode == "barcode_mode":
            new_mode = "real_height_mode"
            mode_text.value = "実測値入力モード"
            page.session.set("real_height_step", 1)
            page.session.set("real_height_input_waiting", True)
            page.side_bar.top_message_text.value = "1件目の商品の実測値を入力してください。"
            page.side_bar.real_height_textfield.visible = True
            page.side_bar.barcode_textfield.visible = False
        else:
            new_mode = "barcode_mode"
            mode_text.value = "通常モード"
            page.session.set("real_height_step", None)
            page.session.set("real_height_input_waiting", None)
            page.side_bar.top_message_text.value = "バーコード自動入力"
            page.side_bar.real_height_textfield.visible = False
            page.side_bar.barcode_textfield.visible = True
        page.session.set("mode", new_mode)
        page.update()

    page.title = "Auto Crop App"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.maximized = True
    
    # デフォルトモードを設定
    page.session.set("mode", "barcode_mode")
    mode_text = ft.Text("通常モード", size=12, style=ft.TextStyle(font_family="Noto Sans CJK JP"))
    
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.PHOTO_CAMERA_OUTLINED),
        leading_width=40,
        title=ft.Text("商品撮影システム", size=12, style=ft.TextStyle(font_family="Noto Sans CJK JP")),
        center_title=False,
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        color=ft.Colors.BLACK,
        actions=[
            mode_text,
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="入力モード切り替え", on_click=change_mode),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(text="システム終了", on_click=terminate),
                ]
            ),
        ],
    )
    image_grid_view = ft.GridView(
        expand=True,
        max_extent=180,         # 画像1枚の最大幅
        child_aspect_ratio=0.4, # 画像の縦横比を調整
        spacing=10,
        run_spacing=10,
    )
    side_bar = SideBar(page, [image_grid_view], None)
    page.side_bar = side_bar

    layout = ft.Row(
        [side_bar, image_grid_view],
        spacing=0,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )

    page.add(layout)
    page.observer = start_watchdog(page, [image_grid_view])
    page.update()

# Fletアプリケーションを実行
if __name__ == "__main__":
    ft.app(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir=os.path.dirname(__file__),
    )