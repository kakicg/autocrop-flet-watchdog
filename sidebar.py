import flet as ft
import time
import random
import colorsys
import os
import sys
import csv
from sqlalchemy.orm import declarative_base
from config import set_PROCESSED_DIR, set_WATCH_DIR, set_PREVIEW_DIR, set_CSV_DIR, get_PROCESSED_DIR, get_WATCH_DIR, get_PREVIEW_DIR, get_CSV_DIR, get_GAMMA, set_GAMMA, get_MARGIN_TOP, get_MARGIN_BOTTOM, get_MARGIN_LEFT, get_MARGIN_RIGHT, set_MARGIN_TOP, set_MARGIN_BOTTOM, set_MARGIN_LEFT, set_MARGIN_RIGHT, get_ASPECT_RATIO, set_ASPECT_RATIO, get_MENU_BAR_VISIBLE, set_MENU_BAR_VISIBLE
from item_db import ItemInfo, session
from datetime import datetime


class SideBar(ft.Container):
    def __init__(self, page:ft.Page, view_controls):
        super().__init__()
        
        def set_item(event):
            # barcode_wholeとしてセット
            barcode_whole = event.control.value
            if barcode_whole == "m":
                # メニューバーの表示/非表示を切り替え
                current_visible = get_MENU_BAR_VISIBLE()
                new_visible = not current_visible
                set_MENU_BAR_VISIBLE(new_visible)
                
                # メニューバーの表示状態を更新
                if hasattr(page, 'popup_menu_button'):
                    page.popup_menu_button.visible = new_visible
                    page.popup_menu_button.update()
                
                # メッセージを表示
                if new_visible:
                    top_message_container.border = ft.border.all(6, ft.Colors.GREEN_100)
                    top_message_container.content.value = "メニューバーを表示しました"
                else:
                    top_message_container.border = ft.border.all(6, ft.Colors.YELLOW_100)
                    top_message_container.content.value = "メニューバーを非表示にしました"
                
                event.control.value = ""
                page.update()
                return
            if barcode_whole == "h":
                # マニュアルの表示/非表示を切り替え
                current_visible = manual_row.visible
                new_visible = not current_visible
                manual_row.visible = new_visible
                
                # 他の設定画面を非表示にする
                if new_visible:
                    self.set_barcode_field_visible(False)
                    self.set_processed_dir_setting_visible(False)
                    self.set_watch_dir_setting_visible(False)
                    self.set_preview_dir_setting_visible(False)
                    self.set_csv_dir_setting_visible(False)
                    self.set_gamma_setting_visible(False)
                    self.set_margin_setting_visible(False)
                    self.set_aspect_ratio_setting_visible(False)
                    top_message_container.border = ft.border.all(6, ft.Colors.BLUE_100)
                    top_message_container.content.value = "操作マニュアルを表示中"
                else:
                    self.set_barcode_field_visible(True)
                    top_message_container.border = ft.border.all(6, ft.Colors.PINK_100)
                    top_message_container.content.value = "バーコード自動入力"
                
                manual_row.update()
                event.control.value = ""
                page.update()
                return
            if barcode_whole == "t":
                # テストモードの切り替え
                current_test_mode = page.session.get('test_mode') or False
                new_test_mode = not current_test_mode
                
                page.session.set('test_mode', new_test_mode)
                
                if new_test_mode:
                    top_message_container.border = ft.border.all(6, ft.Colors.GREEN_100)
                    top_message_container.content.value = "テストモード: 白黒画像を表示します"
                else:
                    top_message_container.border = ft.border.all(6, ft.Colors.PINK_100)
                    top_message_container.content.value = "バーコード自動入力"
                
                # モード表示を更新
                if hasattr(page, 'update_mode_display'):
                    page.update_mode_display()
                
                event.control.value = ""
                page.update()
                return
            # barcode_wholeの長さが0の場合、ランダムな40桁の数字を生成
            if len(barcode_whole) < 1:
                import random
                barcode_whole = ''.join([str(random.randint(0, 9)) for _ in range(40)])
            
            page.session.set("barcode_whole", barcode_whole)
            
            # 再処理モードの場合
            pending_image_data = page.session.get('pending_image_data')
            if pending_image_data:
                # barcode_numberを計算
                import re
                cleaned_barcode = re.sub(r'\D', '', barcode_whole)
                if len(cleaned_barcode) < 38:
                    barcode_number = cleaned_barcode[:5]
                else:
                    barcode_number = cleaned_barcode[33:38]
                
                # 再処理を実行
                reprocess_image_with_barcode(page, pending_image_data, barcode_whole)
                # モードをリセット
                page.session.set('pending_mode', False)
                page.session.set('pending_image_data', None)
                # コンテナのボーダーを削除
                container = pending_image_data['container']
                container.border = None
                container.update()
                
                # メッセージを通常モードに戻す
                page.side_bar.top_message_text.value = "バーコード自動入力"
                
                # テキストフィールドをクリア
                event.control.value = ""
                event.control.update()
                
                # ページを更新してメッセージの変更を反映
                page.update()
                return
            # barcode_numberの設定ロジック
            import re
            cleaned_barcode = re.sub(r'\D', '', barcode_whole)
            if len(cleaned_barcode) < 38:
                barcode_number = cleaned_barcode[:5]
            else:
                barcode_number = cleaned_barcode[33:38]  # 34文字目から5文字
            print(f"barcode_number: {barcode_number}")
            print(f"barcode_whole: {barcode_whole}")
            # 既存のバーコードリストを取得（なければ空リスト）
            barcode_list = page.session.get("barcode_list") or []
            # 重複チェック
            if barcode_number in barcode_list:
                print(f"barcode_number is already in the list: {barcode_number}")

                # 重複: メッセージ表示
                top_message_container.border = ft.border.all(6, ft.Colors.RED_100)
                top_message_container.content.value = f'[ {barcode_number} ] は既に登録済みです'
                event.control.value = ""
                # GridViewから同バーコードの画像カードを削除（ファイル名は {barcode_number}.jpg）
                try:
                    grid_view = page.main_view
                    targets = []
                    for idx, ctrl in enumerate(list(grid_view.controls)):
                        if isinstance(ctrl, ft.Container) and hasattr(ctrl, 'content') and isinstance(ctrl.content, ft.Column):
                            # image_containerの構造: Column -> [Image, text_container]
                            # text_containerの構造: Container -> Column -> [Text(バーコード番号), Text, Text, Text]
                            column_controls = getattr(ctrl.content, 'controls', [])
                            for child in column_controls:
                                # text_containerを探す
                                if isinstance(child, ft.Container) and hasattr(child, 'content') and isinstance(child.content, ft.Column):
                                    text_column = child.content
                                    text_controls = getattr(text_column, 'controls', [])
                                    # 最初のText要素がバーコード番号
                                    if text_controls and isinstance(text_controls[0], ft.Text) and text_controls[0].value == barcode_number:
                                        targets.append(idx)
                                        break
                    for idx in reversed(targets):
                        del grid_view.controls[idx]
                    if targets:
                        grid_view.update()
                        print(f"Removed {len(targets)} duplicate barcode card(s) for {barcode_number}")
                except Exception as e:
                    print(f"Error removing duplicated barcode card: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 重複したbarcode_numberを現在の値として設定し、次の画像入力とマッチできるようにする
                page.session.set("barcode_number", barcode_number)
                top_message_container.border = ft.border.all(6, ft.Colors.BLUE_100)
                top_message_container.content.value = f'[ {barcode_number} ]を撮影中...'
                page.update()
                return  # 重複の場合は処理を終了
            
            # 重複でない: 追加してセッション更新
            barcode_list.append(barcode_number)
            page.session.set("barcode_list", barcode_list)
            page.session.set("barcode_number", barcode_number)
            event.control.value = ""
            
            top_message_container.border = ft.border.all(6, ft.Colors.BLUE_100)
            current_barcode_number = page.session.get("barcode_number")
            top_message_container.content.value = f'[ {current_barcode_number} ]を撮影中...'
            self.middle_lists.insert(0, 
                ft.Container(
                    content=ft.Text(current_barcode_number, 
                                color="black",
                                size=24,
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
        
        def force_focus(evet):
            barcode_textfield.focus()

        def tile_clicked(event):
            index = self.middle_lists.index(event.control)
            # offset_pos = (horizontal_list_view_height + item_title_height) * index
            offset_pos = index * 100
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
            padding=ft.padding.symmetric(vertical=2, horizontal=10),  # ← 縦方向のpaddingを小さく
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
            color=ft.Colors.BLACK,
            dense=True  # ← 追加
        )
        self.real_height_textfield = real_height_textfield
        barcode_textfield = ft.TextField(
            on_submit=set_item,
            on_blur=force_focus,
            border_color=ft.Colors.BLACK,
            cursor_color=ft.Colors.BLACK,
            text_size=6,
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
        def cancel_processed_dir_setting(event):
            self.set_processed_dir_setting_visible(False)
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
        processed_dir_cancel_button = ft.ElevatedButton("キャンセル", on_click=cancel_processed_dir_setting)
        processed_dir_row = ft.Column([
            processed_dir_field,
            ft.Row([
                processed_dir_pick_button, processed_dir_button, processed_dir_cancel_button
            ], alignment=ft.MainAxisAlignment.START, spacing=5)
        ], spacing=5, visible=False)
        def watch_dir_pick_result(e):
            if e.path:
                watch_dir_field.value = e.path
                watch_dir_field.update()
        def update_watch_dir(event):
            set_WATCH_DIR(watch_dir_field.value)
            page.snack_bar = ft.SnackBar(ft.Text("監視フォルダを更新しました。再起動が必要です。"))
            page.snack_bar.open = True
            self.set_watch_dir_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        def cancel_watch_dir_setting(event):
            self.set_watch_dir_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        watch_dir_picker = ft.FilePicker(on_result=watch_dir_pick_result)
        page.overlay.append(watch_dir_picker)
        watch_dir_pick_button = ft.ElevatedButton("参照", on_click=lambda e: watch_dir_picker.get_directory_path())
        watch_dir_button = ft.ElevatedButton("更新", on_click=update_watch_dir)
        watch_dir_cancel_button = ft.ElevatedButton("キャンセル", on_click=cancel_watch_dir_setting)
        watch_dir_row = ft.Column([
            watch_dir_field,
            ft.Row([
                watch_dir_pick_button, watch_dir_button, watch_dir_cancel_button
            ], alignment=ft.MainAxisAlignment.START, spacing=5)
        ], spacing=5, visible=False)
        
        # --- Preview directory settings UI ---
        preview_dir_field = ft.TextField(
            label="プレビューフォルダー (PREVIEW_DIR)",
            value=get_PREVIEW_DIR(),
            width=220,
            dense=True,
        )
        def preview_dir_pick_result(e):
            if e.path:
                preview_dir_field.value = e.path
                preview_dir_field.update()
        def update_preview_dir(event):
            set_PREVIEW_DIR(preview_dir_field.value)
            page.snack_bar = ft.SnackBar(ft.Text("プレビューフォルダーを更新しました。再起動が必要です。"))
            page.snack_bar.open = True
            self.set_preview_dir_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        def cancel_preview_dir_setting(event):
            self.set_preview_dir_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        preview_dir_picker = ft.FilePicker(on_result=preview_dir_pick_result)
        page.overlay.append(preview_dir_picker)
        preview_dir_pick_button = ft.ElevatedButton("参照", on_click=lambda e: preview_dir_picker.get_directory_path())
        preview_dir_button = ft.ElevatedButton("更新", on_click=update_preview_dir)
        preview_dir_cancel_button = ft.ElevatedButton("キャンセル", on_click=cancel_preview_dir_setting)
        preview_dir_row = ft.Column([
            preview_dir_field,
            ft.Row([
                preview_dir_pick_button, preview_dir_button, preview_dir_cancel_button
            ], alignment=ft.MainAxisAlignment.START, spacing=5)
        ], spacing=5, visible=False)
        
        # --- CSV directory settings UI ---
        csv_dir_field = ft.TextField(
            label="CSVフォルダー (CSV_DIR)",
            value=get_CSV_DIR(),
            width=220,
            dense=True,
        )
        def csv_dir_pick_result(e):
            if e.path:
                csv_dir_field.value = e.path
                csv_dir_field.update()
        def update_csv_dir(event):
            set_CSV_DIR(csv_dir_field.value)
            page.snack_bar = ft.SnackBar(ft.Text("CSVフォルダーを更新しました。再起動が必要です。"))
            page.snack_bar.open = True
            self.set_csv_dir_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        def cancel_csv_dir_setting(event):
            self.set_csv_dir_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        csv_dir_picker = ft.FilePicker(on_result=csv_dir_pick_result)
        page.overlay.append(csv_dir_picker)
        csv_dir_pick_button = ft.ElevatedButton("参照", on_click=lambda e: csv_dir_picker.get_directory_path())
        csv_dir_button = ft.ElevatedButton("更新", on_click=update_csv_dir)
        csv_dir_cancel_button = ft.ElevatedButton("キャンセル", on_click=cancel_csv_dir_setting)
        csv_dir_row = ft.Column([
            csv_dir_field,
            ft.Row([
                csv_dir_pick_button, csv_dir_button, csv_dir_cancel_button
            ], alignment=ft.MainAxisAlignment.START, spacing=5)
        ], spacing=5, visible=False)
        
        # --- GAMMA settings UI ---
        gamma_label = ft.Text(
            "GAMMA設定 (コントラスト調整)",
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=12,
        )
        gamma_value_text = ft.Text(
            value=f"{get_GAMMA():.1f}",
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=14,
        )
        def update_gamma_label(value):
            gamma_value_text.value = f"{value:.1f}"
            gamma_value_text.update()
        def on_gamma_change(e):
            gamma_value = e.control.value
            update_gamma_label(gamma_value)
            set_GAMMA(gamma_value)
            page.snack_bar = ft.SnackBar(ft.Text(f"GAMMA値を{gamma_value:.1f}に更新しました。"))
            page.snack_bar.open = True
            page.update()
        gamma_slider = ft.Slider(
            min=1.0,
            max=5.0,
            value=get_GAMMA(),
            divisions=40,  # 0.1刻みで40段階
            on_change=on_gamma_change,
        )
        def update_gamma_setting(event):
            self.set_gamma_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        gamma_cancel_button = ft.ElevatedButton("閉じる", on_click=update_gamma_setting)
        gamma_row = ft.Column([
            gamma_label,
            ft.Row([
                ft.Container(
                    content=gamma_value_text,
                    padding=ft.padding.only(right=10),
                    alignment=ft.alignment.center_right,
                ),
                ft.Container(
                    content=gamma_slider,
                    expand=True,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            ft.Row([
                gamma_cancel_button
            ], alignment=ft.MainAxisAlignment.END, spacing=5)
        ], spacing=10, visible=False)
        
        # --- Margin settings UI ---
        margin_label = ft.Text(
            "マージン設定",
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=12,
        )
        margin_top_value_text = ft.Text(
            value=f"{min(50.0, get_MARGIN_TOP()):.1f}%",  # 50%を超える場合は50%に制限
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=12,
        )
        margin_bottom_value_text = ft.Text(
            value=f"{min(50.0, get_MARGIN_BOTTOM()):.1f}%",  # 50%を超える場合は50%に制限
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=12,
        )
        margin_left_value_text = ft.Text(
            value=f"{min(50.0, get_MARGIN_LEFT()):.1f}%",  # 50%を超える場合は50%に制限
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=12,
        )
        margin_right_value_text = ft.Text(
            value=f"{min(50.0, get_MARGIN_RIGHT()):.1f}%",  # 50%を超える場合は50%に制限
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=12,
        )
        
        def update_margin_top_label(value):
            margin_top_value_text.value = f"{value:.1f}%"
            margin_top_value_text.update()
        def update_margin_bottom_label(value):
            margin_bottom_value_text.value = f"{value:.1f}%"
            margin_bottom_value_text.update()
        def update_margin_left_label(value):
            margin_left_value_text.value = f"{value:.1f}%"
            margin_left_value_text.update()
        def update_margin_right_label(value):
            margin_right_value_text.value = f"{value:.1f}%"
            margin_right_value_text.update()
        
        def on_margin_top_change(e):
            margin_value = e.control.value
            update_margin_top_label(margin_value)
            set_MARGIN_TOP(margin_value)
            page.snack_bar = ft.SnackBar(ft.Text(f"上マージンを{margin_value:.1f}%に更新しました。"))
            page.snack_bar.open = True
            page.update()
        def on_margin_bottom_change(e):
            margin_value = e.control.value
            update_margin_bottom_label(margin_value)
            set_MARGIN_BOTTOM(margin_value)
            page.snack_bar = ft.SnackBar(ft.Text(f"下マージンを{margin_value:.1f}%に更新しました。"))
            page.snack_bar.open = True
            page.update()
        def on_margin_left_change(e):
            margin_value = e.control.value
            update_margin_left_label(margin_value)
            set_MARGIN_LEFT(margin_value)
            page.snack_bar = ft.SnackBar(ft.Text(f"左マージンを{margin_value:.1f}%に更新しました。"))
            page.snack_bar.open = True
            page.update()
        def on_margin_right_change(e):
            margin_value = e.control.value
            update_margin_right_label(margin_value)
            set_MARGIN_RIGHT(margin_value)
            page.snack_bar = ft.SnackBar(ft.Text(f"右マージンを{margin_value:.1f}%に更新しました。"))
            page.snack_bar.open = True
            page.update()
        
        margin_top_slider = ft.Slider(
            min=0,
            max=50,
            value=min(50.0, get_MARGIN_TOP()),  # 50%を超える場合は50%に制限
            divisions=500,  # 0.1%刻みで500段階
            on_change=on_margin_top_change,
        )
        margin_bottom_slider = ft.Slider(
            min=0,
            max=50,
            value=min(50.0, get_MARGIN_BOTTOM()),  # 50%を超える場合は50%に制限
            divisions=500,  # 0.1%刻みで500段階
            on_change=on_margin_bottom_change,
        )
        margin_left_slider = ft.Slider(
            min=0,
            max=50,
            value=min(50.0, get_MARGIN_LEFT()),  # 50%を超える場合は50%に制限
            divisions=500,  # 0.1%刻みで500段階
            on_change=on_margin_left_change,
        )
        margin_right_slider = ft.Slider(
            min=0,
            max=50,
            value=min(50.0, get_MARGIN_RIGHT()),  # 50%を超える場合は50%に制限
            divisions=500,  # 0.1%刻みで500段階
            on_change=on_margin_right_change,
        )
        
        def update_margin_setting(event):
            self.set_margin_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        margin_cancel_button = ft.ElevatedButton("閉じる", on_click=update_margin_setting)
        
        margin_row = ft.Column([
            margin_label,
            ft.Row([
                ft.Text("上:", style=ft.TextStyle(font_family="Noto Sans CJK JP"), size=12),
                ft.Container(
                    content=margin_top_value_text,
                    padding=ft.padding.only(right=10),
                    alignment=ft.alignment.center_right,
                    width=40,
                ),
                ft.Container(
                    content=margin_top_slider,
                    expand=True,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            ft.Row([
                ft.Text("下:", style=ft.TextStyle(font_family="Noto Sans CJK JP"), size=12),
                ft.Container(
                    content=margin_bottom_value_text,
                    padding=ft.padding.only(right=10),
                    alignment=ft.alignment.center_right,
                    width=40,
                ),
                ft.Container(
                    content=margin_bottom_slider,
                    expand=True,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            ft.Row([
                ft.Text("左:", style=ft.TextStyle(font_family="Noto Sans CJK JP"), size=12),
                ft.Container(
                    content=margin_left_value_text,
                    padding=ft.padding.only(right=10),
                    alignment=ft.alignment.center_right,
                    width=40,
                ),
                ft.Container(
                    content=margin_left_slider,
                    expand=True,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            ft.Row([
                ft.Text("右:", style=ft.TextStyle(font_family="Noto Sans CJK JP"), size=12),
                ft.Container(
                    content=margin_right_value_text,
                    padding=ft.padding.only(right=10),
                    alignment=ft.alignment.center_right,
                    width=40,
                ),
                ft.Container(
                    content=margin_right_slider,
                    expand=True,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            ft.Row([
                margin_cancel_button
            ], alignment=ft.MainAxisAlignment.END, spacing=5)
        ], spacing=10, visible=False)
        
        # --- Aspect Ratio settings UI ---
        aspect_ratio_label = ft.Text(
            "縦横比設定",
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=12,
        )
        
        # 現在の縦横比を取得
        current_aspect_ratio = get_ASPECT_RATIO()
        
        # ラジオボタンで縦横比を選択
        aspect_ratio_4_3 = ft.Radio(
            value="4:3",
            label="4:3（縦4横3）",
        )
        aspect_ratio_3_2 = ft.Radio(
            value="3:2",
            label="3:2（縦3横2）",
        )
        aspect_ratio_1_1 = ft.Radio(
            value="1:1",
            label="1:1（正方形）",
        )
        
        def on_aspect_ratio_change(e):
            new_ratio = e.control.value
            set_ASPECT_RATIO(new_ratio)
            page.snack_bar = ft.SnackBar(ft.Text(f"縦横比を{new_ratio}に更新しました。"))
            page.snack_bar.open = True
            page.update()
        
        aspect_ratio_group = ft.RadioGroup(
            content=ft.Column([
                aspect_ratio_4_3,
                aspect_ratio_3_2,
                aspect_ratio_1_1,
            ], spacing=5),
            value=current_aspect_ratio,
            on_change=on_aspect_ratio_change,
        )
        
        def update_aspect_ratio_setting(event):
            self.set_aspect_ratio_setting_visible(False)
            self.set_barcode_field_visible(True)
            page.update()
        aspect_ratio_cancel_button = ft.ElevatedButton("閉じる", on_click=update_aspect_ratio_setting)
        
        aspect_ratio_row = ft.Column([
            aspect_ratio_label,
            aspect_ratio_group,
            ft.Row([
                aspect_ratio_cancel_button
            ], alignment=ft.MainAxisAlignment.END, spacing=5)
        ], spacing=10, visible=False)
        
        # --- Manual display UI ---
        def get_manual_path():
            """PyInstaller/flet pack環境でも正しくMENU_MANUAL.mdを見つける"""
            checked_paths = []
            
            # パッケージ化された環境の場合
            if getattr(sys, 'frozen', False):
                # 1. _MEIPASS（一時展開ディレクトリ）を確認
                if hasattr(sys, '_MEIPASS'):
                    base_path = sys._MEIPASS
                    manual_path = os.path.join(base_path, "MENU_MANUAL.md")
                    checked_paths.append(manual_path)
                    if os.path.exists(manual_path):
                        return manual_path
                
                # 2. 実行ファイルと同じディレクトリを確認
                if hasattr(sys, 'executable'):
                    main_dir = os.path.dirname(sys.executable)
                    manual_path = os.path.join(main_dir, "MENU_MANUAL.md")
                    checked_paths.append(manual_path)
                    if os.path.exists(manual_path):
                        return manual_path
                    
                    # 実行ファイルのディレクトリ内の様々な場所も確認
                    for subdir in ["", "_internal", "lib"]:
                        check_path = os.path.join(main_dir, subdir, "MENU_MANUAL.md")
                        checked_paths.append(check_path)
                        if os.path.exists(check_path):
                            return check_path
            
            # 通常のPython環境の場合
            # 現在のスクリプトのディレクトリを確認
            script_dir = os.path.dirname(os.path.abspath(__file__))
            manual_path = os.path.join(script_dir, "MENU_MANUAL.md")
            checked_paths.append(manual_path)
            if os.path.exists(manual_path):
                return manual_path
            
            # カレントディレクトリも確認
            current_dir = os.getcwd()
            manual_path = os.path.join(current_dir, "MENU_MANUAL.md")
            checked_paths.append(manual_path)
            if os.path.exists(manual_path):
                return manual_path
            
            # 見つからない場合は最後に試したパスを返す（デバッグ情報付き）
            return manual_path
        
        def load_manual_content():
            """MENU_MANUAL.mdの内容を読み込む"""
            manual_path = get_manual_path()
            try:
                if os.path.exists(manual_path):
                    with open(manual_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    # デバッグ情報を追加
                    debug_info = f"マニュアルファイルが見つかりません。\nパス: {manual_path}\n"
                    if getattr(sys, 'frozen', False):
                        debug_info += f"frozen: True\n"
                        if hasattr(sys, '_MEIPASS'):
                            debug_info += f"_MEIPASS: {sys._MEIPASS}\n"
                        if hasattr(sys, 'executable'):
                            debug_info += f"executable: {sys.executable}\n"
                            debug_info += f"executable dir: {os.path.dirname(sys.executable)}\n"
                    else:
                        debug_info += f"frozen: False\n"
                        debug_info += f"script dir: {os.path.dirname(os.path.abspath(__file__))}\n"
                    return debug_info
            except Exception as e:
                return f"マニュアルの読み込みエラー: {e}\nパス: {manual_path}"
        
        manual_content_text = ft.Text(
            value=load_manual_content(),
            style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            size=10,
            selectable=True,
            width=280,
        )
        manual_scroll_view = ft.Container(
            content=ft.ListView(
                controls=[manual_content_text],
                expand=True,
            ),
            expand=True,
            width=280,
            height=500,
        )
        def close_manual(event):
            manual_row.visible = False
            self.set_barcode_field_visible(True)
            top_message_container.border = ft.border.all(6, ft.Colors.PINK_100)
            top_message_container.content.value = "バーコード自動入力"
            manual_row.update()
            page.update()
        manual_close_button = ft.ElevatedButton("閉じる", on_click=close_manual)
        manual_row = ft.Column([
            ft.Text(
                "操作マニュアル",
                style=ft.TextStyle(font_family="Noto Sans CJK JP", weight=ft.FontWeight.BOLD),
                size=14,
            ),
            manual_scroll_view,
            ft.Row([
                manual_close_button
            ], alignment=ft.MainAxisAlignment.END, spacing=5)
        ], spacing=10, visible=False)
        
        dir_settings_column = ft.Column([
            processed_dir_row,
            watch_dir_row,
            preview_dir_row,
            csv_dir_row,
            gamma_row,
            margin_row,
            aspect_ratio_row,
            manual_row,
        ], spacing=5)
        
        self.content = ft.Column(
            controls=[foot_container, dir_settings_column, real_height_textfield, top_message_container, middle_container],
            spacing=10,
            expand=True
        )
        # Store for later control
        self.processed_dir_row = processed_dir_row
        self.watch_dir_row = watch_dir_row
        self.preview_dir_row = preview_dir_row
        self.preview_dir_picker = preview_dir_picker
        self.csv_dir_row = csv_dir_row
        self.csv_dir_picker = csv_dir_picker
        self.gamma_row = gamma_row
        self.gamma_slider = gamma_slider
        self.gamma_value_text = gamma_value_text
        self.margin_row = margin_row
        self.margin_top_slider = margin_top_slider
        self.margin_bottom_slider = margin_bottom_slider
        self.margin_left_slider = margin_left_slider
        self.margin_right_slider = margin_right_slider
        self.margin_top_value_text = margin_top_value_text
        self.margin_bottom_value_text = margin_bottom_value_text
        self.margin_left_value_text = margin_left_value_text
        self.margin_right_value_text = margin_right_value_text
        self.aspect_ratio_row = aspect_ratio_row
        self.aspect_ratio_group = aspect_ratio_group
        self.processed_dir_picker = processed_dir_picker
        self.watch_dir_picker = watch_dir_picker
        self.barcode_textfield = barcode_textfield
        self.top_message_text = top_message_text
        self.top_message_container = top_message_container

    def set_barcode_field_visible(self, visible: bool):
        self.barcode_textfield.visible = visible
        self.barcode_textfield.update()

    def set_processed_dir_setting_visible(self, visible: bool):
        self.processed_dir_row.visible = visible
        self.processed_dir_row.update()

    def set_watch_dir_setting_visible(self, visible: bool):
        self.watch_dir_row.visible = visible
        self.watch_dir_row.update()
    
    def set_preview_dir_setting_visible(self, visible: bool):
        self.preview_dir_row.visible = visible
        self.preview_dir_row.update()
    
    def set_csv_dir_setting_visible(self, visible: bool):
        self.csv_dir_row.visible = visible
        self.csv_dir_row.update()
    
    def set_gamma_setting_visible(self, visible: bool):
        self.gamma_row.visible = visible
        if visible:
            # 表示時に現在の値を反映
            current_gamma = get_GAMMA()
            self.gamma_slider.value = current_gamma
            self.gamma_value_text.value = f"{current_gamma:.1f}"
        self.gamma_row.update()
    
    def set_margin_setting_visible(self, visible: bool):
        self.margin_row.visible = visible
        if visible:
            # 表示時に現在の値を反映（50%を超える場合は50%に制限）
            current_margin_top = min(50.0, get_MARGIN_TOP())
            current_margin_bottom = min(50.0, get_MARGIN_BOTTOM())
            current_margin_left = min(50.0, get_MARGIN_LEFT())
            current_margin_right = min(50.0, get_MARGIN_RIGHT())
            self.margin_top_slider.value = current_margin_top
            self.margin_bottom_slider.value = current_margin_bottom
            self.margin_left_slider.value = current_margin_left
            self.margin_right_slider.value = current_margin_right
            self.margin_top_value_text.value = f"{current_margin_top:.1f}%"
            self.margin_bottom_value_text.value = f"{current_margin_bottom:.1f}%"
            self.margin_left_value_text.value = f"{current_margin_left:.1f}%"
            self.margin_right_value_text.value = f"{current_margin_right:.1f}%"
            self.margin_top_value_text.update()
            self.margin_bottom_value_text.update()
            self.margin_left_value_text.update()
            self.margin_right_value_text.update()
        self.margin_row.update()
    
    def set_aspect_ratio_setting_visible(self, visible: bool):
        self.aspect_ratio_row.visible = visible
        if visible:
            # 表示時に現在の値を反映
            current_aspect_ratio = get_ASPECT_RATIO()
            self.aspect_ratio_group.value = current_aspect_ratio
        self.aspect_ratio_row.update()

def reprocess_image_with_barcode(page, image_data, barcode_whole):
    """バーコード未入力画像の再処理"""
    try:
        # barcode_numberを計算
        import re
        cleaned_barcode = re.sub(r'\D', '', barcode_whole)
        if len(cleaned_barcode) < 38:
            barcode_number = cleaned_barcode[:5]
        else:
            barcode_number = cleaned_barcode[33:38]
        
        # ファイルパスを再構築
        root_folder_path = page.session.get("root_folder_path")
        barcode_prefix = barcode_number[:2] if len(barcode_number) >= 2 else "XX"
        barcode_folder_path = os.path.join(root_folder_path, barcode_prefix)
        os.makedirs(barcode_folder_path, exist_ok=True)
        
        # 新しいファイルパス
        new_processed_name = f"{barcode_number}.jpg"
        new_processed_path = os.path.join(barcode_folder_path, new_processed_name)
        
        # ファイルを移動（既に移動されている場合は現在のパスを確認）
        import shutil
        old_processed_path = image_data['processed_path']
        old_barcode_number = image_data.get('barcode_number')  # 既存のバーコード番号を取得
        
        # ファイルが存在しない場合、データベースから最新のパスを取得
        if not os.path.exists(old_processed_path):
            # データベースから同じoriginal_urlの最新のレコードを検索
            latest_item = session.query(ItemInfo).filter(
                ItemInfo.original_url == image_data.get('image_path')
            ).order_by(ItemInfo.id.desc()).first()
            
            if latest_item and latest_item.precessed_url and os.path.exists(latest_item.precessed_url):
                # データベースに記録されている最新のパスを使用
                old_processed_path = latest_item.precessed_url
                # 古いバーコード番号も取得（パスから抽出）
                old_barcode_from_path = os.path.splitext(os.path.basename(old_processed_path))[0]
                if old_barcode_from_path and old_barcode_from_path != 'unknown':
                    old_barcode_number = old_barcode_from_path
                print(f"データベースから最新のパスを取得: {old_processed_path}")
            elif os.path.exists(new_processed_path):
                # 既に移動済みの場合は、そのまま使用
                old_processed_path = new_processed_path
                print(f"既に移動済みのファイルを使用: {new_processed_path}")
            else:
                # ファイルが見つからない場合はエラー
                raise FileNotFoundError(f"処理済みファイルが見つかりません: {image_data['processed_path']}")
        
        # 古いバーコード番号が存在し、新しいバーコード番号と異なる場合、古いCSVファイルを削除
        if old_barcode_number and old_barcode_number != barcode_number:
            # CSV_DIR内の古いCSVファイルを削除
            csv_dir = get_CSV_DIR()
            root_folder_name = os.path.basename(root_folder_path)
            old_barcode_prefix = old_barcode_number[:2] if len(old_barcode_number) >= 2 else "XX"
            csv_root_folder_path = os.path.join(csv_dir, root_folder_name)
            old_csv_barcode_folder_path = os.path.join(csv_root_folder_path, old_barcode_prefix)
            old_csv_file_path = os.path.join(old_csv_barcode_folder_path, f"{old_barcode_number}.csv")
            if os.path.exists(old_csv_file_path):
                try:
                    os.remove(old_csv_file_path)
                    print(f"古いCSVファイルを削除: {old_csv_file_path}")
                except Exception as e:
                    print(f"古いCSVファイルの削除エラー: {e}")
        
        # ファイルが存在し、新しいパスと異なる場合のみ移動
        if os.path.exists(old_processed_path) and old_processed_path != new_processed_path:
            # 既に新しいパスにファイルが存在する場合は削除してから移動
            if os.path.exists(new_processed_path):
                os.remove(new_processed_path)
            shutil.move(old_processed_path, new_processed_path)
            print(f"ファイルを移動: {old_processed_path} -> {new_processed_path}")
        
        # image_dataを更新して、次回の再処理に備える
        image_data['processed_path'] = new_processed_path
        image_data['barcode_number'] = barcode_number  # バーコード番号も保存
        
        # page.sessionのpending_image_dataも更新（次回クリック時に正しいパスが使われるように）
        current_pending = page.session.get('pending_image_data')
        if current_pending and current_pending.get('container') == image_data.get('container'):
            page.session.set('pending_image_data', image_data)
        
        # CSVファイルに書き込み（CSV_DIR内に書き込む）
        csv_dir = get_CSV_DIR()
        root_folder_name = os.path.basename(root_folder_path)
        csv_root_folder_path = os.path.join(csv_dir, root_folder_name)
        os.makedirs(csv_root_folder_path, exist_ok=True)
        
        # barcode_prefixフォルダを作成
        csv_barcode_folder_path = os.path.join(csv_root_folder_path, barcode_prefix)
        os.makedirs(csv_barcode_folder_path, exist_ok=True)
        
        # barcode_number.csvを書き込み
        csv_file_path = os.path.join(csv_barcode_folder_path, f"{barcode_number}.csv")
        file_exists = os.path.exists(csv_file_path)
        
        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['バーコード', '高さ', '時刻']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'バーコード': barcode_whole,
                '高さ': image_data['estimated_height'],
                '時刻': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # 親ディレクトリ（root_folder_name）のCSVファイルにもアペンド
        parent_csv_path = os.path.join(csv_root_folder_path, f"{root_folder_name}.csv")
        parent_file_exists = os.path.exists(parent_csv_path)
        
        with open(parent_csv_path, 'a', newline='', encoding='utf-8') as parent_csvfile:
            parent_writer = csv.DictWriter(parent_csvfile, fieldnames=fieldnames)
            
            if not parent_file_exists:
                parent_writer.writeheader()
            
            parent_writer.writerow({
                'バーコード': barcode_whole,
                '高さ': image_data['estimated_height'],
                '時刻': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # データベースを更新
        new_item = ItemInfo(
            barcode=barcode_number,
            barcode_whole=barcode_whole,
            precessed_url=new_processed_path,
            original_url=image_data['image_path'],
            height=int(image_data['estimated_height']),
            top_y=None,
            real_height=None
        )
        session.add(new_item)
        session.commit()
        
        # GridViewコンテナの表示を更新
        container = image_data['container']
        # テキストを正常なバーコード表示に変更
        # 新しい構造では、text_container内のft.Column内のft.Textを探す
        if hasattr(container, 'content') and isinstance(container.content, ft.Column):
            for child in container.content.controls:
                # text_container（ft.Container）を探す
                if isinstance(child, ft.Container) and hasattr(child, 'content'):
                    if isinstance(child.content, ft.Column):
                        # 最初のText要素（バーコード番号表示）を更新
                        text_items = [item for item in child.content.controls if isinstance(item, ft.Text)]
                        if text_items:
                            # 最初のText要素がバーコード番号表示
                            first_text = text_items[0]
                            first_text.value = barcode_number
                            first_text.color = ft.Colors.WHITE
                            break
        
        # サイドバーにバーコード番号を追加
        page.side_bar.middle_lists.insert(0, 
            ft.Container(
                content=ft.Text(barcode_number, 
                            color="white",
                            size=24,
                        ),
                bgcolor="#3DBCE2",
                expand=True,
                margin=8,
                padding=8
            ),
        )
        
        # サイドバーから「バーコード未入力」の表示を削除
        preview_name = image_data['preview_name']
        targets_to_remove = []
        for idx, container in enumerate(page.side_bar.middle_lists):
            if isinstance(container, ft.Container) and hasattr(container, 'content'):
                content = container.content
                if isinstance(content, ft.Text) and f"バーコード未入力（{preview_name}）" in content.value:
                    targets_to_remove.append(idx)
        
        # 後ろから削除（インデックスがずれないように）
        for idx in reversed(targets_to_remove):
            del page.side_bar.middle_lists[idx]
        
        # UI更新
        container.update()
        page.update()
        
        print(f"再処理完了: {barcode_number}")
        
    except Exception as e:
        print(f"再処理エラー: {e}")

