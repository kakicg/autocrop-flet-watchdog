import flet as ft
import time
import random
import colorsys
from sqlalchemy.orm import declarative_base
from config import set_PROCESSED_DIR, set_WATCH_DIR, get_PROCESSED_DIR, get_WATCH_DIR


class SideBar(ft.Container):
    def __init__(self, page:ft.Page, view_controls):
        super().__init__()
        
        def set_item(event):
            page.session.set("barcode_number", event.control.value)
            event.control.value = ""
            
            top_message_container.border = ft.border.all(6, ft.Colors.BLUE_100)
            current_barcode_number = page.session.get("barcode_number")
            top_message_container.content.value = f'[ {current_barcode_number} ]を撮影中...'
            self.middle_lists.insert(0, 
                ft.Container(
                    content=ft.Text(current_barcode_number, 
                                color="black",
                            ),
                    bgcolor="#ffffe0",
                    expand=True,
                    # on_click=tile_clicked,
                    margin=8,
                    padding=8
                ),
            )
            page.main_view.scroll_to(offset=0, duration=1000)
            page.update()

        def set_real_height(event):
            page.session.set("real_height", event.control.value)
            event.control.value = ""
            # 入力欄を非表示、メッセージ切り替え
            page.session.set("real_height_input_waiting", False)
            step = page.session.get("real_height_step")
            self.real_height_textfield.visible = False
            self.top_message_text.value = f"{step}件目の商品の撮影を行ってください"
            page.update()

        def next_item(event):
            page.session.set("barcode_number", "")
            barcode_textfield.visible = True
            top_message_container.border = ft.border.all(6, ft.Colors.PINK_100)
            top_message_container.content.value = 'バーコードを読み取ってください'
            page.update()
        
        def force_focus(evet):
            barcode_textfield.focus()

        def tile_clicked(event):
            index = self.middle_lists.index(event.control)
            offset_pos = (horizontal_list_view_height + item_title_height) * index
            page.main_view.scroll_to(offset=offset_pos, duration=1000)
           
        # 上部の固定コンポーネント (A)
        top_message_text = ft.Text(
            "バーコード自動入力", 
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
        self.middle_lists = middle_container.controls
        # 下部の固定コンポーネント (C)

        real_height_textfield = ft.TextField(
            on_submit=set_real_height,
            on_blur=force_focus,
            text_size=14,
            autofocus=False,
            visible=False,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK
        )
        barcode_textfield = ft.TextField(
            on_submit=set_item,
            on_blur=force_focus,
            border_color=ft.Colors.BLUE_GREY_700,
            cursor_color=ft.Colors.BLUE_GREY_700,
            text_size=8,
            autofocus=True,
            visible=True
        )
        
        foot_column = ft.Column(
            controls=[real_height_textfield, barcode_textfield],
            spacing=10,
            width=float('inf')
        )
        foot_container = ft.Container(
            content=foot_column,
            padding=0,
            width=float('inf')
        )
        # --- Directory settings UI ---
        processed_dir_field = ft.TextField(
            label="保存先ディレクトリ (PROCESSED_DIR)",
            value=get_PROCESSED_DIR(),
            width=220,
            dense=True,
        )
        watch_dir_field = ft.TextField(
            label="監視フォルダ (WATCH_DIR)",
            value=get_WATCH_DIR(),
            width=220,
            dense=True,
        )
        def update_processed_dir(event):
            set_PROCESSED_DIR(processed_dir_field.value)
            page.snack_bar = ft.SnackBar(ft.Text("保存先ディレクトリを更新しました。再起動が必要です。"))
            page.snack_bar.open = True
            self.set_processed_dir_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        def update_watch_dir(event):
            set_WATCH_DIR(watch_dir_field.value)
            page.snack_bar = ft.SnackBar(ft.Text("監視フォルダを更新しました。再起動が必要です。"))
            page.snack_bar.open = True
            self.set_watch_dir_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        def processed_dir_pick_result(e):
            if e.path:
                processed_dir_field.value = e.path
                processed_dir_field.update()
        processed_dir_picker = ft.FilePicker(on_result=processed_dir_pick_result)
        page.overlay.append(processed_dir_picker)
        processed_dir_pick_button = ft.ElevatedButton("参照", on_click=lambda e: processed_dir_picker.get_directory_path())
        processed_dir_button = ft.ElevatedButton("更新", on_click=update_processed_dir)
        processed_dir_row = ft.Row([processed_dir_field, processed_dir_pick_button, processed_dir_button], alignment=ft.MainAxisAlignment.START, visible=False)
        def watch_dir_pick_result(e):
            if e.path:
                watch_dir_field.value = e.path
                watch_dir_field.update()
        watch_dir_picker = ft.FilePicker(on_result=watch_dir_pick_result)
        page.overlay.append(watch_dir_picker)
        watch_dir_pick_button = ft.ElevatedButton("参照", on_click=lambda e: watch_dir_picker.get_directory_path())
        watch_dir_button = ft.ElevatedButton("更新", on_click=update_watch_dir)
        watch_dir_row = ft.Row([watch_dir_field, watch_dir_pick_button, watch_dir_button], alignment=ft.MainAxisAlignment.START, visible=False)
        dir_settings_column = ft.Column([
            processed_dir_row,
            watch_dir_row,
        ], spacing=5)
        # ---
        # Columnを使ってA, B, C, directory settingsを縦に配置
        self.content = ft.Column(
            controls=[top_message_container, middle_container, foot_container, dir_settings_column],
            spacing=10,
            expand=True
        )
        # Store for later control
        self.processed_dir_row = processed_dir_row
        self.watch_dir_row = watch_dir_row
        self.processed_dir_picker = processed_dir_picker
        self.watch_dir_picker = watch_dir_picker
        self.barcode_textfield = barcode_textfield
        self.top_message_text = top_message_text

    def set_barcode_field_visible(self, visible: bool):
        self.barcode_textfield.visible = visible
        self.barcode_textfield.update()

    def set_processed_dir_setting_visible(self, visible: bool):
        self.processed_dir_row.visible = visible
        self.processed_dir_row.update()

    def set_watch_dir_setting_visible(self, visible: bool):
        self.watch_dir_row.visible = visible
        self.watch_dir_row.update()

