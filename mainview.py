import flet as ft

class MainView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        
        self.expand = 1  # 親として全体に広がる
        self.spacing = 0
        self.scroll = ft.ScrollMode.AUTO
        self.bgcolor = ft.Colors.BLACK
        self.padding = ft.padding.only(left=20, top=10)
        self.margin = ft.margin.symmetric(horizontal=5)

        # GridViewは親に広がるように設定
        # grid_view = ft.GridView(
        #     expand=1,
        #     runs_count=5,
        #     max_extent=150,
        #     child_aspect_ratio=0.66,
        #     spacing=5,
        #     run_spacing=5,
        #     auto_scroll=True
        # )
        grid_view = ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=150,
            child_aspect_ratio=0.66,
            spacing=5,
            run_spacing=5,
        )

        self.content = grid_view
        self.view_controls = grid_view.controls
        self.controls.append(grid_view)