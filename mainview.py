import flet as ft

class MainView(ft.Container):
    def __init__(self, page:ft.Page):
        super().__init__()
        # カンマを除去し、プロパティを正しく設定
        list_view = ft.ListView(
            # expand = True,
            # padding = ft.padding.only(top=40),
            # auto_scroll = True
            height = 300
        )
        self.content = list_view
        self.expand = True
        self.height = float('inf')
        self.bgcolor = ft.colors.BLACK
        self.padding = ft.padding.only(left=20, top=10)  # 左と上だけ余白を設定
        self.margin = ft.margin.symmetric(horizontal=5)  # 左右に5pxの余白
        self.view_controls = list_view.controls

 
