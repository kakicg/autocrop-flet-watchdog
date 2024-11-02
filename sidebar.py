import flet as ft
from monitor_process import monitor_and_process
from jtext import JText
import time

class SideBar(ft.Container):
    def __init__(self, page:ft.Page, view_controls):
        super().__init__()
        def set_item(event):
            page.session.set("camera_loop", True)
            page.session.set("barcode_number", event.control.value)
            page.session.set("current_angle", 0)
            event.control.value = ""
            barcode_textfield.visible = False
            next_button.visible = True
            top_message_container.border = ft.border.all(6, ft.colors.BLUE_100)
            top_message_container.content.value = f'[ {page.session.get("barcode_number")} ]を撮影中...'
            
            page.update()
            monitor_and_process(page, gridview.controls)
            # while page.session.get("camera_loop"):
            #     current_angle = page.session.get("current_angle")
            #     current_angle += 1
            #     print(f"{current_angle} アングル")
            #     gridview.controls.insert(
            #         0,
            #         ft.Image(
            #             src=f"https://picsum.photos/200/300?{current_angle}",
            #             fit=ft.ImageFit.NONE,
            #             repeat=ft.ImageRepeat.NO_REPEAT,
            #             border_radius=ft.border_radius.all(10),
            #         )
            #     )
            #     page.session.set("current_angle", current_angle)
            #     page.update()
            #     time.sleep(3)

        def next_item(event):
            page.session.set("camera_loop", False)
            barcode_textfield.visible = True
            next_button.visible = False
            top_message_container.border = ft.border.all(6, ft.colors.PINK_100)
            top_message_container.content.value = 'バーコードを読み取ってください'
            page.update()
        
        def force_focus(evet):
            barcode_textfield.focus()
           
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
        middle_container = ft.Container(
            content=ft.Text("B: 中央で伸縮", color=ft.colors.WHITE),
            expand=True,  # ここで上下に伸縮させる
            padding=10,
            width=float('inf')
        )

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
            spacing=10,  # コンポーネント間の余白
            width=float('inf')  # サイドバー全体をページにフィットさせる
        )
        foot_container = ft.Container(
            content=foot_column,
            padding=0,
            width=float('inf')
        )
        gridview = ft.GridView(
                expand=1,
                runs_count=5,
                max_extent=200,
                child_aspect_ratio=0.5625,
                spacing=30,
                run_spacing=10,
        ) 
        view_controls.insert(0, gridview)

        # Columnを使ってA, B, Cを縦に配置
        self.content = ft.Column(
            controls=[top_message_container, middle_container, foot_container],
            spacing=10,  # コンポーネント間の余白
            expand=True  # サイドバー全体をページにフィットさせる
        )

        # サイドバーのスタイル
        self.width = 400  # サイドバーの幅
        self.height = float('inf')  # 縦に最大限伸ばす
        self.bgcolor = ft.colors.BLUE_GREY_800
        self.padding = ft.padding.all(10)  # サイドバーの内側余白
        self.margin = ft.margin.all(0)  # サイドバーの外側余白
        self.top_message_text = top_message_text
        self.foot_container = foot_container
        self.barcode_textfield = barcode_textfield

