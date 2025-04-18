import flet as ft
import time
import random
import colorsys


class SideBar(ft.Container):
    def __init__(self, page:ft.Page, view_controls, main_view):
        super().__init__()
        def set_item(event):
            def random_color_hex(
                    hue_range=(0.0,1.0), 
                    saturation_range=(0.15,0.2), 
                    value_range=(0.95,1.0)
                ):
                # Hue (色相), Saturation (彩度), Value (明度) をランダムに生成
                h = random.uniform(*hue_range)          # 色相：0.0～1.0
                s = random.uniform(*saturation_range)  # 彩度：例 0.5～1.0
                v = random.uniform(*value_range)       # 明度：例 0.8～1.0

                # HSVからRGBに変換 (結果は0～1)
                r, g, b = colorsys.hsv_to_rgb(h, s, v)

                # RGB値を0～255に変換
                r, g, b = int(r * 255), int(g * 255), int(b * 255)

                # 16進数 (6桁) にフォーマット
                hex_color = f"#{r:02x}{g:02x}{b:02x}"

                return hex_color
            
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
            
            top_message_container.border = ft.border.all(6, ft.colors.BLUE_100)
            current_barcode_number = page.session.get("barcode_number")
            top_message_container.content.value = f'[ {current_barcode_number} ]を撮影中...'
            new_color = random_color_hex()
            middle_lists.insert(0, 
                ft.Container(
                    content=ft.Text(current_barcode_number, 
                                color="black",
                            ),
                    bgcolor=new_color,
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
            top_message_container.border = ft.border.all(6, ft.colors.PINK_100)
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
            color = ft.colors.WHITE,
            size=14,
        )
        top_message_container = ft.Container(
            content=top_message_text,
            padding=10,
            width=float('inf'),
            border = ft.border.all(6, ft.colors.PINK_100)
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
            border_color=ft.colors.BLUE_GREY_700,
            cursor_color=ft.colors.BLUE_GREY_700,
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
        self.bgcolor = ft.colors.BLUE_GREY_800
        self.padding = ft.padding.all(10)
        self.margin = ft.margin.all(0)
        self.top_message_text = top_message_text
        self.foot_container = foot_container
        self.barcode_textfield = barcode_textfield
        self.middle_lists = middle_lists
        item_title_height = 40
        horizontal_list_view_height = 320
            

