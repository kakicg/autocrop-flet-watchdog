import flet as ft

def main(page: ft.Page):
    page.title = "GridView Example"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 50
    page.update()

    images = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=200,
        child_aspect_ratio=0.5625,
        spacing=15,
        run_spacing=15,
    )

    page.add(images)

    for i in range(0, 60):
        images.controls.insert(0,
            ft.Column(
                [
                    ft.Image(
                    src=f"https://picsum.photos/200/300?{i}",
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    # border_radius=ft.border_radius.all(10),
                    ),
                    ft.Text(
                        f"Number:{i}",
                        size=10,
                        color=ft.colors.WHITE,
                        weight=ft.FontWeight.W_100,
                    ),
                ]
            )
            
        )
    page.update()

ft.app(main, view=ft.AppView.WEB_BROWSER)