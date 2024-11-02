import flet as ft
import os
def main(page: ft.Page):
    path = "./processed_images/111_1.jpg"
    abspath = os.path.abspath(path)
    page.add(ft.Image(src=path))
    page.update()

ft.app(
    main,
    view=ft.AppView.WEB_BROWSER,
    assets_dir=os.path.dirname(__file__),
)