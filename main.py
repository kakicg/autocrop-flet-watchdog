import flet as ft
from sidebar import SideBar
from mainview import MainView
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

    page.title = "Auto Crop App"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.maximized = True
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.PHOTO_CAMERA_OUTLINED),
        leading_width=40,
        title=ft.Text("商品撮影システム", size=12, style=ft.TextStyle(font_family="Noto Sans CJK JP")),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="システム終了", on_click=terminate),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(
                        text="Checked item", checked=True
                    ),
                ]
            ),
        ],
    )
    main_view = MainView(page)
    side_bar = SideBar(page, main_view.view_controls, main_view.content)

    layout = ft.Row(
        [side_bar, main_view],
        spacing=0,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )

    # レイアウトをページに追加
    page.add(layout)
    
    # Watchdogを起動
    page.observer = start_watchdog(page, main_view.view_controls)
    
    page.update()

# Fletアプリケーションを実行
if __name__ == "__main__":
    ft.app(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir=os.path.dirname(__file__),
    )