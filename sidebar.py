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
            "バーコードを読み取ってください", 
            style = ft.TextStyle(font_family="Noto Sans CJK JP"),
            color = ft.Colors.WHITE,
            size=14,
        )
        top_message_container = ft.Container(
            content=top_message_text,
            padding=10,
            width=float('inf'),
            border = ft.border.all(6, ft.Colors.PINK_100)
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
        # Columnを使ってA, B, Cを縦に配置
        self.content = ft.Column(
            controls=[top_message_container, middle_container, foot_container],
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
        item_title_height = 40
        horizontal_list_view_height = 320

