import flet as ft
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from image_processing import process_image
from item_db import ItemInfo, session
import time
from datetime import datetime
from config import get_PROCESSED_DIR, get_WATCH_DIR, get_A, get_B, set_A_B, increment_TOTAL_SHOTS
import csv
from config import get_GAMMA

text_style = ft.TextStyle(font_family="Noto Sans CJK JP")

class ImageHandler(FileSystemEventHandler):
    def __init__(self, page, view_controls):
        self.page = page
        self.view_controls = view_controls
        self.processed_files = set()
        self.current_angle = 0
        self.last_barcode = None

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            time.sleep(0.5)  # ファイルの書き込み完了を待つ
            self.process_image(event.src_path)

    def process_image(self, image_path):
        if image_path in self.processed_files:
            return
        
        self.processed_files.add(image_path)
        current_mode = self.page.session.get('mode')
        barcode_number = self.page.session.get('barcode_number')
        barcode_whole = self.page.session.get('barcode_whole')
        preview_name = os.path.basename(image_path)
        if barcode_number:
            processed_name = f"{barcode_number}.jpg"
            self.page.session.set('barcode_number', None)
            self.page.session.set('barcode_whole', None)
            # --- SideBarのmiddle_listsを更新 ---
            if hasattr(self.page, 'side_bar'):
                for container in self.page.side_bar.middle_lists:
                    if isinstance(container, ft.Container) and hasattr(container, 'content'):
                        content = container.content
                        if isinstance(content, ft.Text) and content.value == barcode_number:
                            container.bgcolor = "#3DBCE2"
                            content.color = "white"
                            break
            self.page.side_bar.top_message_text.value = f"{barcode_number}の撮影完了"
        else:
            processed_name = preview_name
            self.page.side_bar.top_message_text.value = f"{preview_name}に対応するバーコードが未入力"
            # --- SideBarのmiddle_listsに未入力の表示を追加（赤地・白文字） ---
            if hasattr(self.page, 'side_bar') and hasattr(self.page.side_bar, 'middle_lists'):
                try:
                    self.page.side_bar.middle_lists.insert(
                        0,
                        ft.Container(
                            content=ft.Text(
                                f"バーコード未入力（{preview_name}）",
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=ft.Colors.RED,
                            expand=True,
                            margin=8,
                            padding=8,
                        ),
                    )
                    self.page.update()
                except Exception as e:
                    print(f"Error adding 'バーコード未入力' to sidebar: {e}")

        real_height = self.page.session.get('real_height')
        session_processed_dir = self.page.session.get('processed_dir')

        root_folder_path = self.page.session.get("root_folder_path")
        
        # barcode_numberの先頭2文字のフォルダを作成
        if barcode_number and len(barcode_number) >= 2:
            barcode_prefix = barcode_number[:2]
        else:
            barcode_prefix = "XX"  # フォールバック
        
        barcode_folder_path = os.path.join(root_folder_path, barcode_prefix)
        os.makedirs(barcode_folder_path, exist_ok=True)  # バーコード先頭2文字フォルダを作成
        
        output_file_path = os.path.join(barcode_folder_path, processed_name)

        top_y, estimated_height, processed_path, preview_path, test_path = process_image(
            image_path, 
            output_file_path, 
            preview_name
        )
        
        # 累計撮影枚数をインクリメント
        increment_TOTAL_SHOTS()
        
        # 累計撮影枚数の表示を更新
        if hasattr(self.page, 'update_shot_count_display'):
            self.page.update_shot_count_display()
        
        new_item = ItemInfo(
            barcode=barcode_number if barcode_number else "unknown",
            barcode_whole=barcode_whole if barcode_whole else None,
            precessed_url=processed_path,
            original_url=image_path,
            height=int(estimated_height),
            top_y=int(top_y) if top_y is not None else None,
            real_height=int(real_height) if real_height is not None else None
        )
        session.add(new_item)
        session.commit()

        # CSVファイルに商品データを書き込み（barcode_numberがある場合のみ）
        if barcode_number:
            try:
                csv_file_path = os.path.join(barcode_folder_path, f"{barcode_number}.csv")
                file_exists = os.path.exists(csv_file_path)
                
                with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['バーコード', '高さ', '時刻']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # ファイルが新規作成の場合はヘッダーを書き込み
                    if not file_exists:
                        writer.writeheader()
                    
                    # データを書き込み
                    writer.writerow({
                        'バーコード': barcode_whole if barcode_whole else 'unknown',
                        '高さ': estimated_height,
                        '時刻': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                print(f"CSVデータが '{csv_file_path}' に書き込まれました。")
                
                # 親ディレクトリ（root_folder_name）のCSVファイルにもアペンド
                root_folder_path = self.page.session.get("root_folder_path")
                if root_folder_path:
                    root_folder_name = os.path.basename(root_folder_path)
                    parent_csv_path = os.path.join(root_folder_path, f"{root_folder_name}.csv")
                    parent_file_exists = os.path.exists(parent_csv_path)
                    
                    with open(parent_csv_path, 'a', newline='', encoding='utf-8') as parent_csvfile:
                        parent_writer = csv.DictWriter(parent_csvfile, fieldnames=fieldnames)
                        
                        # ファイルが新規作成の場合はヘッダーを書き込み
                        if not parent_file_exists:
                            parent_writer.writeheader()
                        
                        # データを書き込み
                        parent_writer.writerow({
                            'バーコード': barcode_whole if barcode_whole else 'unknown',
                            '高さ': estimated_height,
                            '時刻': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                    
                    print(f"CSVデータが親ディレクトリ '{parent_csv_path}' にも書き込まれました。")
            except Exception as e:
                print(f"CSV書き込みエラー: {e}")

        if real_height:
            # 直近のtop_y, real_heightペアを2つ取得
            recent_items = session.query(ItemInfo).filter(ItemInfo.top_y != None, ItemInfo.real_height != None).order_by(ItemInfo.id.desc()).limit(2).all()
            if len(recent_items) == 2:
                ty1, rh1 = recent_items[0].top_y, recent_items[0].real_height
                ty2, rh2 = recent_items[1].top_y, recent_items[1].real_height
                # 連立方程式を解く
                if ty1 != ty2:
                    a = (rh1 - rh2) / (ty1 - ty2)
                    b = rh1 - a * ty1
                    set_A_B(a, b)
            self.page.session.set("real_height", None)


        # 画像の絶対パスを取得
        abs_processed_path = os.path.abspath(processed_path)
        abs_preview_path = os.path.abspath(preview_path)
        abs_test_path = os.path.abspath(test_path)


        # オリジナル画像を削除
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"Error deleting original image: {e}")

        # 現在のタイムスタンプを取得
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ラベル表示用のテキストと色（バーコード未入力時は赤字）
        label_text = barcode_number if barcode_number else f"バーコード未入力"
        label_color = ft.Colors.WHITE if barcode_number else ft.Colors.RED
        
        # クリックハンドラーを定義
        def on_image_container_click(event):
            if not barcode_number:  # バーコード未入力の場合のみ
                current_mode = self.page.session.get('pending_mode') or False
                
                if not current_mode:
                    # バーコード入力モードに切り替え
                    self.page.session.set('pending_mode', True)
                    # 対象画像データを保存
                    image_data = {
                        'image_path': image_path,
                        'processed_path': processed_path,
                        'preview_path': preview_path,
                        'estimated_height': estimated_height,
                        'preview_name': preview_name,
                        'container': image_container
                    }
                    self.page.session.set('pending_image_data', image_data)
                    
                    # クリックされたコンテナにボーダーを追加
                    image_container.border = ft.border.all(3, ft.Colors.RED)
                    image_container.update()
                    
                    # メッセージを更新
                    self.page.side_bar.top_message_text.value = f"バーコード入力モード: {preview_name}のバーコードを入力してください"
                    
                    # バーコード入力フィールドを表示・フォーカス
                    self.page.side_bar.barcode_textfield.visible = True
                    self.page.side_bar.barcode_textfield.focus()
                    self.page.update()
                else:
                    # キャンセルモード
                    self.page.session.set('pending_mode', False)
                    self.page.session.set('pending_image_data', None)
                    
                    # クリックされたコンテナのボーダーを削除
                    image_container.border = None
                    image_container.update()
                    
                    # メッセージを元に戻す
                    self.page.side_bar.top_message_text.value = "バーコード自動入力"
                    
                    # バーコード入力フィールドを表示（通常モード継続可能に）
                    self.page.side_bar.barcode_textfield.visible = True
                    self.page.side_bar.barcode_textfield.focus()
                    self.page.update()
        
        text_container = ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        f"{label_text}",
                                        size=18,  # 1.5倍に拡大
                                        color=label_color,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Text(
                                        f"{preview_name}",
                                        style=text_style,
                                        size=12,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Text(
                                        f"推定高さ:{estimated_height}",
                                        style=text_style,
                                        size=18,  # 1.5倍に拡大
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Text(
                                        f"[ {current_time} ]",
                                        style=text_style,
                                        size=10,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_100,
                                    ),
                                ]
                            ),
                        )
        test_text_container = ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        f"【高さ推定用マスク】",
                                        size=12,
                                        color=ft.Colors.YELLOW,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Text(
                                        f"{preview_name}",
                                        style=text_style,
                                        size=12,
                                        color=ft.Colors.YELLOW,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Text(
                                        f"ガンマ値:{get_GAMMA()}",
                                        style=text_style,
                                        size=12,
                                        color=ft.Colors.YELLOW,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Text(
                                        f"[ {current_time} ]",
                                        style=text_style,
                                        size=10,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_100,
                                    ),
                                ]
                            ),
                        )
        # 新しい画像コンテナを作成
        def create_image_container(image_path, text_container):
            return ft.Container(
                        content=ft.Column(
                            [
                                ft.Image(
                                    src=image_path,
                                    fit=ft.ImageFit.CONTAIN,
                                    repeat=ft.ImageRepeat.NO_REPEAT,
                                    height=300,  # 1.5倍に拡大
                                ),
                                text_container,
                            ],
                            spacing=5,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.BLUE_GREY_800,
                        border_radius=10,
                        margin=5,
                        height=450,
                        on_click=on_image_container_click if not barcode_number else None,  # バーコード未入力の場合のみクリック可能
                    )
                
        # image_container = create_image_container(abs_preview_path, text_container)
        image_container = create_image_container(abs_preview_path, text_container)
        test_image_container = create_image_container(abs_test_path, test_text_container)

        try:
            # メインビューのコントロールに追加
            
            grid_view = self.view_controls[0]

            if self.page.session.get('test_mode'):
                grid_view.controls.insert(0, test_image_container)

            grid_view.controls.insert(0, image_container)
            grid_view.update()

            if barcode_number:
                self.page.session.set('barcode_number', '')
                self.last_barcode = None

            self.page.update()

            # --- 実測値入力モードの段階的処理 ---
            if current_mode == "real_height_mode":
                step = self.page.session.get("real_height_step")
                input_waiting = self.page.session.get("real_height_input_waiting")
                if step == 1 and not input_waiting:
                    # 1件目の撮影完了
                    self.page.side_bar.top_message_text.value = "1件目の商品の実測値登録が完了しました。\n引き続き2件目の商品の実測値を入力してください。"
                    self.page.session.set("real_height_step", 2)
                    self.page.session.set("real_height_input_waiting", True)
                    self.page.side_bar.real_height_textfield.visible = True
                    self.page.update()
                elif step == 2 and not input_waiting:
                    # 2件目の撮影完了
                    self.page.side_bar.top_message_text.value = "2件目の商品の実測値登録が完了しました。"
                    self.page.update()
                    import time
                    time.sleep(3)
                    self.page.session.set("mode", "barcode_mode")
                    self.page.session.set("real_height_step", None)
                    self.page.session.set("real_height_input_waiting", None)
                    self.page.side_bar.top_message_text.value = "バーコード自動入力"
                    self.page.side_bar.real_height_textfield.visible = False
                    self.page.side_bar.barcode_textfield.visible = True
                    # モード表示を更新
                    if hasattr(self.page, 'update_mode_display'):
                        self.page.update_mode_display()
                    self.page.update()
                
        except Exception as e:
            print(f"Error updating UI: {e}")

def start_watchdog(page: ft.Page, view_controls):
    watch_dir = get_WATCH_DIR()
    os.makedirs(watch_dir, exist_ok=True)
    event_handler = ImageHandler(page, view_controls)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    return observer 