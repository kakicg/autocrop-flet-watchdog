import flet as ft

class JText(ft.Text):
    def __init__(
            self,
            style=None,
            color=ft.Colors.WHITE,
            **kwargs
        ):
        # デフォルトのスタイルを設定（もしstyleが指定されていない場合）
        if style is None:
            style = ft.TextStyle(font_family="Noto Sans CJK JP")
        
        super().__init__(
            style=style,
            color=color,
            **kwargs
        )