import flet as ft
import time
import random
import colorsys
from sqlalchemy.orm import declarative_base


class SideBar(ft.Container):
    def __init__(self, page:ft.Page, view_controls, main_view):
        super().__init__()
        def set_item(event):
            
            page.session.set("barcode_number", event.control.value)
            event.control.value = ""
            
            # モードに応じてUIを更新
            current_mode = page.session.get("mode")
            if current_mode == "multi_angle":
                barcode_textfield.visible = False
                next_button.visible = True
            else:
                barcode_textfield.visible = True
                next_button.visible = False
            
            top_message_container.border = ft.border.all(6, ft.Colors.BLUE_100)
            current_barcode_number = page.session.get("barcode_number")
            top_message_container.content.value = f'[ {current_barcode_number} ]を撮影中...'
            middle_lists.insert(0, 
                ft.Container(
                    content=ft.Text(current_barcode_number, 
                                color="black",
                            ),
                    bgcolor="#ffffe0",
                    expand=True,
                    on_click=tile_clicked,
                    margin=8,
                    padding=8
                ),
            )
            horizontal_list_view = ft.ListView(
                horizontal=True,
                height=horizontal_list_view_height,
            )
            main_view.scroll_to(offset=0, duration=1000)
            page.update()

        def next_item(event):
            page.session.set("barcode_number", "")
            barcode_textfield.visible = True
            next_button.visible = False
            top_message_container.border = ft.border.all(6, ft.Colors.PINK_100)
            top_message_container.content.value = 'バーコードを読み取ってください'
            page.update()
        
        def force_focus(evet):
            barcode_textfield.focus()

        def tile_clicked(event):
            index = middle_lists.index(event.control)
            offset_pos = (horizontal_list_view_height + item_title_height) * index
            main_view.scroll_to(offset=offset_pos, duration=1000)
           
        # 上部の固定コンポーネント (A)
        top_message_text = ft.Text(
            "自動撮影モード", 
            style = ft.TextStyle(font_family="Noto Sans CJK JP"),
            color = ft.Colors.WHITE,
            size=14,
        )
        top_message_container = ft.Container(
            content=top_message_text,
            padding=10,
            width=float('inf'),
            border = ft.border.all(6, ft.Colors.BLUE_100)
        )
        # 中央の伸縮コンポーネント (B)
        middle_container = ft.ListView(
            divider_thickness = 1,
            expand=True,
            padding=7,
            width=float('inf'),
        )
        middle_lists = middle_container.controls
        # 下部の固定コンポーネント (C)
        barcode_textfield = ft.TextField(
            on_submit=set_item,
            on_blur=force_focus,
            border_color=ft.Colors.BLUE_GREY_700,
            cursor_color=ft.Colors.BLUE_GREY_700,
            text_size=8,
            autofocus=True,
            visible=True
        )
        next_button = ft.CupertinoFilledButton(
            content=ft.Text("次の商品撮影へ"),
            opacity_on_click=0.3,
            on_click=next_item,
            width=float('inf'),
            visible=False
        )
        foot_column = ft.Column(
            controls=[barcode_textfield, next_button],
            spacing=10,
            width=float('inf')
        )
        foot_container = ft.Container(
            content=foot_column,
            padding=0,
            width=float('inf')
        )
        # 実測値設定用UI
        self.calib_prompt = ft.Text(
            "実測値設定モード: 2つの商品画像の推定値と実測値を入力してください。",
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            color=ft.Colors.WHITE,
            size=14,
        )
        self.x1_input = ft.TextField(label="推定値1", width=120)
        self.y1_input = ft.TextField(label="実測値1", width=120)
        self.x2_input = ft.TextField(label="推定値2", width=120)
        self.y2_input = ft.TextField(label="実測値2", width=120)
        self.set_ab_button = ft.ElevatedButton("A,Bを計算して設定", on_click=self.set_ab)
        self.calib_result = ft.Text("", color=ft.Colors.YELLOW, size=12)
        self.calib_column = ft.Column([
            self.calib_prompt,
            ft.Row([self.x1_input, self.y1_input]),
            ft.Row([self.x2_input, self.y2_input]),
            self.set_ab_button,
            self.calib_result
        ], visible=False)
        # Columnを使ってA, B, C, calib_columnを縦に配置
        self.content = ft.Column(
            controls=[top_message_container, middle_container, self.calib_column, foot_container],
            spacing=10,
            expand=True
        )

        # サイドバーのスタイル
        self.width = 300
        self.height = float('inf')
        self.bgcolor = ft.Colors.BLUE_GREY_800
        self.padding = ft.padding.all(10)
        self.margin = ft.margin.all(0)
        self.top_message_text = top_message_text
        self.foot_container = foot_container
        self.barcode_textfield = barcode_textfield
        self.middle_lists = middle_lists
        self.calib_column = self.calib_column
        item_title_height = 40
        horizontal_list_view_height = 320
        # モード切替時のUI更新
        def update_mode():
            mode = page.session.get("mode")
            if mode == "calibration":
                middle_container.visible = False
                self.calib_column.visible = True
            else:
                middle_container.visible = True
                self.calib_column.visible = False
            self.update()
        page.on_session_change = lambda _: update_mode()
        update_mode()
            
    def set_ab(self, event):
        try:
            x1 = float(self.x1_input.value)
            y1 = float(self.y1_input.value)
            x2 = float(self.x2_input.value)
            y2 = float(self.y2_input.value)
            if x1 == x2:
                self.calib_result.value = "推定値1と推定値2は異なる値にしてください。"
                self.update()
                return
            from image_processing import A, B
            A_new = (y2 - y1) / (x2 - x1)
            B_new = y1 - A_new * x1
            import image_processing
            image_processing.A = A_new
            image_processing.B = B_new
            self.calib_result.value = f"A={A_new:.4f}, B={B_new:.2f} を設定しました。"
        except Exception as e:
            self.calib_result.value = f"エラー: {e}"
        self.update()

