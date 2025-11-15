import flet as ft
from sidebar import SideBar
from watchdog_process import start_watchdog
import optparse
import os
import asyncio
import sys
import time
from config import get_PROCESSED_DIR, get_PREVIEW_DIR, initialize_settings, get_TOTAL_SHOTS, get_SHOT_COUNT_START_DATE, reset_TOTAL_SHOTS, get_MENU_BAR_VISIBLE
from version import VERSION

# アプリケーション起動時に設定を初期化（新しい項目があれば追加）
initialize_settings()

if sys.stdout is None:
    import io
    sys.stdout = io.StringIO()
if sys.stderr is None:
    import io
    sys.stderr = io.StringIO()

def main(page: ft.Page):
    directory_settings_mode = {"active": False}  # Use dict for mutability in closures
    def terminate(event):
        page.session.set("camera_loop", False)
        if hasattr(page, 'observer'):
            page.observer.stop()
            page.observer.join()
        page.window.close()

    def update_mode_display():
        """現在のモード状態に基づいてメニューバーのモード表示を更新"""
        current_mode = page.session.get("mode") or "barcode_mode"
        test_mode = page.session.get('test_mode') or False
        
        if current_mode == "real_height_mode":
            if test_mode:
                mode_text.value = "実測値入力モード + テストモード"
            else:
                mode_text.value = "実測値入力モード"
        else:  # barcode_mode
            if test_mode:
                mode_text.value = "テストモード"
            else:
                mode_text.value = "通常モード"
        # mode_text.update()は削除（page.update()で更新される）
    
    def change_mode(event):
        print(f"change_mode: {page.session.get('mode')}")
        current_mode = page.session.get("mode")

        if current_mode is None or current_mode == "barcode_mode":
            new_mode = "real_height_mode"
            page.session.set("real_height_step", 1)
            page.session.set("real_height_input_waiting", True)
            page.side_bar.top_message_text.value = "1件目の商品の実測値を入力してください。"
            page.side_bar.real_height_textfield.visible = True
            page.side_bar.barcode_textfield.visible = False
        else:
            new_mode = "barcode_mode"
            page.session.set("real_height_step", None)
            page.session.set("real_height_input_waiting", None)
            page.side_bar.top_message_text.value = "バーコード自動入力"
            page.side_bar.real_height_textfield.visible = False
            page.side_bar.barcode_textfield.visible = True
        page.session.set("mode", new_mode)
        update_mode_display()
        page.update()
    
    def toggle_test_mode(event):
        """テストモードの切り替え"""
        current_test_mode = page.session.get('test_mode') or False
        new_test_mode = not current_test_mode
        
        page.session.set('test_mode', new_test_mode)
        
        if new_test_mode:
            page.side_bar.top_message_text.value = "テストモード: 白黒画像を表示します"
        else:
            page.side_bar.top_message_text.value = "バーコード自動入力"
        
        update_mode_display()
        page.update()

    def open_processed_dir_setting(event):
        page.side_bar.set_barcode_field_visible(False)
        page.side_bar.set_processed_dir_setting_visible(True)
        page.side_bar.set_watch_dir_setting_visible(False)
        page.side_bar.set_preview_dir_setting_visible(False)
        page.side_bar.set_gamma_setting_visible(False)
        page.side_bar.set_margin_setting_visible(False)
        page.side_bar.set_aspect_ratio_setting_visible(False)
        page.side_bar.top_message_text.value = "保存先ディレクトリ設定モードです。設定後は再起動してください。"
        page.update()

    def open_watch_dir_setting(event):
        page.side_bar.set_barcode_field_visible(False)
        page.side_bar.set_processed_dir_setting_visible(False)
        page.side_bar.set_watch_dir_setting_visible(True)
        page.side_bar.set_preview_dir_setting_visible(False)
        page.side_bar.set_gamma_setting_visible(False)
        page.side_bar.set_margin_setting_visible(False)
        page.side_bar.set_aspect_ratio_setting_visible(False)
        page.side_bar.top_message_text.value = "監視フォルダ設定モードです。設定後は再起動してください。"
        page.update()
    
    def open_preview_dir_setting(event):
        page.side_bar.set_barcode_field_visible(False)
        page.side_bar.set_processed_dir_setting_visible(False)
        page.side_bar.set_watch_dir_setting_visible(False)
        page.side_bar.set_preview_dir_setting_visible(True)
        page.side_bar.set_gamma_setting_visible(False)
        page.side_bar.set_margin_setting_visible(False)
        page.side_bar.set_aspect_ratio_setting_visible(False)
        page.side_bar.top_message_text.value = "プレビューフォルダー設定モードです。設定後は再起動してください。"
        page.update()
    
    def open_gamma_setting(event):
        page.side_bar.set_barcode_field_visible(False)
        page.side_bar.set_processed_dir_setting_visible(False)
        page.side_bar.set_watch_dir_setting_visible(False)
        page.side_bar.set_preview_dir_setting_visible(False)
        page.side_bar.set_gamma_setting_visible(True)
        page.side_bar.set_margin_setting_visible(False)
        page.side_bar.set_aspect_ratio_setting_visible(False)
        page.side_bar.top_message_text.value = "GAMMA設定モードです。スライダーでコントラスト調整値を変更できます。"
        page.update()
    
    def open_margin_setting(event):
        page.side_bar.set_barcode_field_visible(False)
        page.side_bar.set_processed_dir_setting_visible(False)
        page.side_bar.set_watch_dir_setting_visible(False)
        page.side_bar.set_preview_dir_setting_visible(False)
        page.side_bar.set_gamma_setting_visible(False)
        page.side_bar.set_margin_setting_visible(True)
        page.side_bar.set_aspect_ratio_setting_visible(False)
        page.side_bar.top_message_text.value = "マージン設定モードです。上下左右のマージン幅を変更できます。"
        page.update()
    
    def open_aspect_ratio_setting(event):
        page.side_bar.set_barcode_field_visible(False)
        page.side_bar.set_processed_dir_setting_visible(False)
        page.side_bar.set_watch_dir_setting_visible(False)
        page.side_bar.set_preview_dir_setting_visible(False)
        page.side_bar.set_gamma_setting_visible(False)
        page.side_bar.set_margin_setting_visible(False)
        page.side_bar.set_aspect_ratio_setting_visible(True)
        page.side_bar.top_message_text.value = "縦横比設定モードです。4:3、3:2、1:1から選択できます。"
        page.update()
    
    def reset_shot_count(event):
        """累計撮影枚数をリセット"""
        reset_TOTAL_SHOTS()
        update_shot_count_display()
        page.side_bar.top_message_text.value = "累計撮影枚数をリセットしました。"
        page.update()
    
    def update_shot_count_display():
        """累計撮影枚数の表示を更新"""
        total_shots = get_TOTAL_SHOTS()
        start_date = get_SHOT_COUNT_START_DATE()
        shot_count_text.value = f"累計撮影: {total_shots}枚 (起算日: {start_date})"
        page.update()

    page.title = f"Auto Crop App v{VERSION}"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.maximized = True
    
    # デフォルトモードを設定
    page.session.set("mode", "barcode_mode")
    # テストモードを初期化（デフォルトはFalse）
    page.session.set("test_mode", False)
    # バーコード履歴リストを初期化
    page.session.set("barcode_list", [])
    # processed_dir をセッションに保持
    page.session.set("processed_dir", get_PROCESSED_DIR())
    
    # day.txtから先頭8文字を読み取り、root_folderを作成・設定
    processed_dir = get_PROCESSED_DIR()
    day_txt_path = os.path.join(processed_dir, "day.txt")
    root_folder_name = ""
    
    try:
        if os.path.exists(day_txt_path):
            with open(day_txt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                root_folder_name = content[:8]  # 先頭8文字
        else:
            # day.txtが存在しない場合は100年後の今日の日付を使用
            from datetime import datetime, timedelta
            future_date = datetime.now() + timedelta(days=36525)  # 100年後（365.25日 × 100年）
            root_folder_name = future_date.strftime("%Y%m%d")
    except Exception as e:
        print(f"Error reading day.txt: {e}")
        # エラー時は100年後の今日の日付を使用
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=36525)  # 100年後（365.25日 × 100年）
        root_folder_name = future_date.strftime("%Y%m%d")
    
    # root_folderを作成
    root_folder_path = os.path.join(processed_dir, root_folder_name)
    os.makedirs(root_folder_path, exist_ok=True)
    
    # page.sessionに設定
    page.session.set("root_folder_path", root_folder_path)
    
    # previewフォルダ内の10日以上前のファイルを削除
    try:
        preview_dir = get_PREVIEW_DIR()
        if os.path.exists(preview_dir):
            current_time = time.time()
            ten_days_ago = current_time - (10 * 24 * 60 * 60)  # 10日前のタイムスタンプ
            
            for filename in os.listdir(preview_dir):
                file_path = os.path.join(preview_dir, filename)
                if os.path.isfile(file_path):
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime < ten_days_ago:
                        os.remove(file_path)
                        print(f"古いファイルを削除: {file_path}")
    except Exception as e:
        print(f"previewフォルダのクリーンアップエラー: {e}")
    
    mode_text = ft.Text("通常モード", size=12, style=ft.TextStyle(font_family="Noto Sans CJK JP", weight=ft.FontWeight.BOLD))
    mode_text_container = ft.Container(
        content=mode_text,
        margin=ft.margin.only(left=40, right=40)
    )
    shot_count_text = ft.Text("", size=10, style=ft.TextStyle(font_family="Noto Sans CJK JP"))
    
    # メニューバーの表示設定を取得
    menu_bar_visible = get_MENU_BAR_VISIBLE()
    
    # PopupMenuButtonを作成（設定に基づいて表示/非表示を制御）
    popup_menu_button = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(text="実測値入力モード", on_click=change_mode),
            ft.PopupMenuItem(text="テストモード切り替え", on_click=toggle_test_mode),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="監視フォルダーの設定", on_click=open_watch_dir_setting),
            ft.PopupMenuItem(text="書き込みフォルダーの設定", on_click=open_processed_dir_setting),
            ft.PopupMenuItem(text="プレビューフォルダーの設定", on_click=open_preview_dir_setting),
            ft.PopupMenuItem(text="GAMMA設定（コントラスト調整）", on_click=open_gamma_setting),
            ft.PopupMenuItem(text="マージン設定", on_click=open_margin_setting),
            ft.PopupMenuItem(text="縦横比設定", on_click=open_aspect_ratio_setting),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="累計撮影枚数をリセット", on_click=reset_shot_count),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="システム終了", on_click=terminate),
        ],
        visible=menu_bar_visible
    )
    
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.PHOTO_CAMERA_OUTLINED),
        leading_width=40,
        title=ft.Text(f"商品撮影システム v{VERSION}", size=12, style=ft.TextStyle(font_family="Noto Sans CJK JP")),
        center_title=False,
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        color=ft.Colors.BLACK,
        actions=[
            shot_count_text,
            mode_text_container,
            popup_menu_button,
        ],
    )
    main_view = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=150,
        child_aspect_ratio=0.66,
        spacing=5,
        run_spacing=5,
    )
    main_view = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=225,  # 1.5倍に拡大
        child_aspect_ratio=0.45,
        spacing=5,
        run_spacing=5,
    )
    side_bar = SideBar(page, main_view.controls)
    side_bar.width = 300
    page.side_bar = side_bar
    page.main_view = main_view
    page.mode_text = mode_text
    page.mode_text_container = mode_text_container
    page.shot_count_text = shot_count_text
    page.update_mode_display = update_mode_display
    page.update_shot_count_display = update_shot_count_display
    page.popup_menu_button = popup_menu_button

    layout = ft.Row(
        [main_view, side_bar],
        spacing=0,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )

    page.add(layout)
    page.observer = start_watchdog(page, [main_view])
    
    # 初期モード表示を更新（page.add()の後に実行）
    update_mode_display()
    update_shot_count_display()
    page.update()

# Fletアプリケーションを実行
if __name__ == "__main__":
   ft.app(target=main, view=ft.FLET_APP)
    