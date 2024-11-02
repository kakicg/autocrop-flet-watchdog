import flet as ft

class MainView(ft.Container):
    def __init__(self, page:ft.Page):
        super().__init__()
        # カンマを除去し、プロパティを正しく設定
        view_column = ft.Column(
            expand = True,
            height = float('inf')
        )
        self.content = view_column
        self.expand = True
        self.height = float('inf')
        self.bgcolor = ft.colors.BLACK
        self.padding = ft.padding.only(left=20, top=10)  # 左と上だけ余白を設定
        self.margin = ft.margin.symmetric(horizontal=5)  # 左右に5pxの余白
        self.view_controls = view_column.controls

 
