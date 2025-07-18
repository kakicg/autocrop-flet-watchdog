import flet as ft
from sidebar import SideBar
from watchdog_process import start_watchdog
import optparse
import os
import asyncio
import sys

if sys.stdout is None:
    import io
    sys.stdout = io.StringIO()
if sys.stderr is None:
    import io
    sys.stderr = io.StringIO()

def main(page: ft.Page):
    directory_settings_mode = {"active": False}  # Use dict for mutability in closures
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

    def open_processed_dir_setting(event):
        page.side_bar.set_barcode_field_visible(False)
        page.side_bar.set_processed_dir_setting_visible(True)
        page.side_bar.set_watch_dir_setting_visible(False)
        page.side_bar.top_message_text.value = "保存先ディレクトリ設定モードです。設定後は再起動してください。"
        page.update()

    def open_watch_dir_setting(event):
        page.side_bar.set_barcode_field_visible(False)
        page.side_bar.set_processed_dir_setting_visible(False)
        page.side_bar.set_watch_dir_setting_visible(True)
        page.side_bar.top_message_text.value = "監視フォルダ設定モードです。設定後は再起動してください。"
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
                    ft.PopupMenuItem(text="実測値入力モード", on_click=change_mode),
                    ft.PopupMenuItem(text="監視フォルダーの設定", on_click=open_watch_dir_setting),
                    ft.PopupMenuItem(text="書き込みフォルダーの設定", on_click=open_processed_dir_setting),
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
        child_aspect_ratio=0.66,
        spacing=5,
        run_spacing=5,
    )
    main_view = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=150,
        child_aspect_ratio=0.45,
        spacing=5,
        run_spacing=5,
    )
    side_bar = SideBar(page, main_view.controls)
    side_bar.width = 300
    page.side_bar = side_bar
    page.main_view = main_view

    layout = ft.Row(
        [main_view, side_bar],
        spacing=0,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )

    page.add(layout)
    page.observer = start_watchdog(page, [main_view])
    page.update()

# Fletアプリケーションを実行
if __name__ == "__main__":
   ft.app(target=main, view=ft.FLET_APP)
    