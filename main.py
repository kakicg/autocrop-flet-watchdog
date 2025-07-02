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
        current_mode = page.session.get("mode")
        if current_mode is None or current_mode == "barcode_mode":
            new_mode = "real_height_mode"
            mode_text.value = "モード: 実測値入力モード"
            # 実測値入力モード: 実測値欄を可視化、バーコード欄を不可視化
            page.side_bar.real_height_textfield.visible = True
            page.side_bar.barcode_textfield.visible = False
        else:
            new_mode = "barcode_mode"
            mode_text.value = "モード: 通常モード"
            # 通常モード: バーコード欄を可視化、実測値欄を不可視化
            page.side_bar.real_height_textfield.visible = False
            page.side_bar.barcode_textfield.visible = True
        page.session.set("mode", new_mode)
        page.update()

    page.title = "Auto Crop App"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.maximized = True
    
    # デフォルトモードを設定
    page.session.set("mode", "single_angle")
    mode_text = ft.Text("通常モード", size=12, style=ft.TextStyle(font_family="Noto Sans CJK JP"))
    
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.PHOTO_CAMERA_OUTLINED),
        leading_width=40,
        title=ft.Text("商品撮影システム", size=12, style=ft.TextStyle(font_family="Noto Sans CJK JP")),
        center_title=False,
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        actions=[
            mode_text,
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="実測値入力", on_click=change_mode),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(text="システム終了", on_click=terminate),
                ]
            ),
        ],
    )
    main_view = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=150,
        child_aspect_ratio=0.45,
        spacing=5,
        run_spacing=5,
    )
    side_bar = SideBar(page, main_view.controls, main_view)
    page.side_bar = side_bar

    layout = ft.Row(
        [side_bar, main_view],
        spacing=0,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )

    # レイアウトをページに追加
    page.add(layout)
    
    # Watchdogを起動
    page.observer = start_watchdog(page, main_view.controls)
    
    page.update()

# Fletアプリケーションを実行
if __name__ == "__main__":
    ft.app(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir=os.path.dirname(__file__),
    )