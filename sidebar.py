import flet as ft
import time
import random
import colorsys
import os
import csv
from sqlalchemy.orm import declarative_base
from config import set_PROCESSED_DIR, set_WATCH_DIR, get_PROCESSED_DIR, get_WATCH_DIR
from item_db import ItemInfo, session
from datetime import datetime


class SideBar(ft.Container):
    def __init__(self, page:ft.Page, view_controls):
        super().__init__()
        
        def set_item(event):
            # barcode_wholeとしてセット
            barcode_whole = event.control.value
            
            # barcode_wholeの長さが5未満の場合、ランダムな40桁の数字を生成
            if len(barcode_whole) < 5:
                import random
                barcode_whole = ''.join([str(random.randint(0, 9)) for _ in range(40)])
            
            page.session.set("barcode_whole", barcode_whole)
            
            # 再処理モードの場合
            pending_image_data = page.session.get('pending_image_data')
            if pending_image_data:
                # 再処理を実行
                reprocess_image_with_barcode(page, pending_image_data, barcode_whole)
                # モードをリセット
                page.session.set('pending_mode', False)
                page.session.set('pending_image_data', None)
                # コンテナのボーダーを削除
                container = pending_image_data['container']
                container.border = None
                container.update()
                
                # メッセージを更新
                page.side_bar.top_message_text.value = f"{barcode_number}の再処理が完了しました"
                page.side_bar.top_message_container.border = ft.border.all(6, ft.Colors.BLUE_100)
                
                # テキストフィールドをクリア
                event.control.value = ""
                event.control.update()
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
                            for child in getattr(ctrl.content, 'controls', []):
                                if isinstance(child, ft.Text) and child.value == barcode_number:
                                    targets.append(idx)
                                    break
                    for idx in reversed(targets):
                        del grid_view.controls[idx]
                    if targets:
                        grid_view.update()
                except Exception as e:
                    print(f"Error removing duplicated barcode card: {e}")
                page.update()
            else:
                barcode_list.append(barcode_number)

                
            # 重複でない: 追加してセッション更新
            
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
        dir_settings_column = ft.Column([
            processed_dir_row,
            watch_dir_row,
        ], spacing=5)
        
        self.content = ft.Column(
            controls=[foot_container, dir_settings_column, real_height_textfield, top_message_container, middle_container],
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
        
        # ファイルを移動
        import shutil
        shutil.move(image_data['processed_path'], new_processed_path)
        
        # CSVファイルに書き込み
        csv_file_path = os.path.join(barcode_folder_path, f"{barcode_number}.csv")
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
        for child in container.content.controls:
            if isinstance(child, ft.Text) and child.color == ft.Colors.RED:
                child.value = barcode_number
                child.color = ft.Colors.WHITE
                break
        
        # サイドバーにバーコード番号を追加
        page.side_bar.middle_lists.insert(0, 
            ft.Container(
                content=ft.Text(barcode_number, 
                            color="black",
                            size=24,
                        ),
                bgcolor="#3DBCE2",
                expand=True,
                margin=8,
                padding=8
            ),
        )
        
        # UI更新
        container.update()
        page.update()
        
        print(f"再処理完了: {barcode_number}")
        
    except Exception as e:
        print(f"再処理エラー: {e}")

