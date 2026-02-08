import flet as ft
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import json
import time
from pathlib import Path
from typing import Optional, List

# 設定ファイルのパス
VIEWER_SETTINGS_FILE = "viewer_settings.json"

def load_viewer_settings():
    """viewer設定を読み込む"""
    if os.path.exists(VIEWER_SETTINGS_FILE):
        with open(VIEWER_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "preview_dir": "",
        "main_app_dir": ""
    }

def save_viewer_settings(settings):
    """viewer設定を保存"""
    with open(VIEWER_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def get_settings_from_main_app(main_app_dir: str) -> Optional[dict]:
    """main.pyアプリのsettings.jsonを読み込む"""
    if not main_app_dir:
        return None
    settings_path = os.path.join(main_app_dir, "settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"settings.json読み込みエラー: {e}")
    return None

def resolve_preview_dir(preview_dir: str, main_app_dir: str = "") -> str:
    """preview_dirのパスを解決（相対パスの場合は絶対パスに変換）"""
    if not preview_dir:
        return ""
    
    # 既に絶対パスの場合
    if os.path.isabs(preview_dir):
        return preview_dir
    
    # 相対パスの場合
    if main_app_dir:
        # main_app_dirからの相対パスとして解決
        resolved = os.path.join(main_app_dir, preview_dir)
        if os.path.exists(resolved):
            return os.path.abspath(resolved)
    
    # 現在の作業ディレクトリからの相対パスとして解決
    resolved = os.path.abspath(preview_dir)
    return resolved

def get_latest_images(preview_dir: str, count: int = 2) -> List[str]:
    """監視フォルダーから最新の画像ファイルを取得"""
    if not preview_dir or not os.path.exists(preview_dir):
        return []
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    image_files = []
    
    for filename in os.listdir(preview_dir):
        file_path = os.path.join(preview_dir, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(image_extensions):
            image_files.append(file_path)
    
    # 更新日時でソート（新しい順）
    image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    return image_files[:count]

class ImageViewerHandler(FileSystemEventHandler):
    """画像フォルダーの変更を監視するハンドラー"""
    def __init__(self, page, preview_dir):
        self.page = page
        self.preview_dir = preview_dir
        self.last_update_time = 0
        self.update_interval = 0.5  # 0.5秒間隔で更新
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                # ファイルの書き込み完了を待つ
                time.sleep(0.5)
                self.update_images()
    
    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                current_time = time.time()
                # 更新間隔を制御
                if current_time - self.last_update_time > self.update_interval:
                    self.last_update_time = current_time
                    self.update_images()
    
    def update_images(self):
        """画像を更新"""
        if hasattr(self.page, 'update_images'):
            self.page.update_images()

def main(page: ft.Page):
    # 設定を読み込む
    viewer_settings = load_viewer_settings()
    preview_dir = viewer_settings.get("preview_dir", "")
    main_app_dir = viewer_settings.get("main_app_dir", "")
    
    # main.pyアプリのsettings.jsonからpreview_dirを取得（設定されていない場合）
    if not preview_dir and main_app_dir:
        main_settings = get_settings_from_main_app(main_app_dir)
        if main_settings and "PREVIEW_DIR" in main_settings:
            preview_dir = resolve_preview_dir(main_settings["PREVIEW_DIR"], main_app_dir)
    
    # 画像表示用のコントロール
    image1 = ft.Image(
        src="",
        fit=ft.ImageFit.CONTAIN,
        expand=True,
    )
    image2 = ft.Image(
        src="",
        fit=ft.ImageFit.CONTAIN,
        expand=True,
    )
    
    image_container1 = ft.Container(
        content=image1,
        expand=True,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.BLACK,
    )
    
    image_container2 = ft.Container(
        content=image2,
        expand=True,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.BLACK,
    )
    
    # 設定ダイアログ
    preview_dir_textfield = ft.TextField(
        label="プレビューフォルダー（preview_dir）",
        value=preview_dir,
        expand=True,
    )
    
    main_app_dir_textfield = ft.TextField(
        label="main.pyアプリのフォルダー（settings.jsonの場所）",
        value=main_app_dir,
        expand=True,
    )
    
    settings_dialog = ft.AlertDialog(
        title=ft.Text("設定", style=ft.TextStyle(font_family="Noto Sans CJK JP")),
        content=ft.Container(
            content=ft.Column(
                [
                    preview_dir_textfield,
                    main_app_dir_textfield,
                    ft.Text(
                        "※ main.pyアプリのフォルダーを設定すると、そのsettings.jsonからPREVIEW_DIRを自動取得します。",
                        size=12,
                        color=ft.Colors.GREY_600,
                        style=ft.TextStyle(font_family="Noto Sans CJK JP"),
                    ),
                ],
                spacing=10,
                tight=True,
            ),
            width=500,
            padding=20,
        ),
        actions=[
            ft.TextButton(
                "キャンセル",
                on_click=lambda e: close_settings_dialog(),
            ),
            ft.TextButton(
                "保存",
                on_click=lambda e: save_settings(),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_settings_dialog(e):
        """設定ダイアログを開く"""
        preview_dir_textfield.value = preview_dir
        main_app_dir_textfield.value = main_app_dir
        page.dialog = settings_dialog
        settings_dialog.open = True
        page.update()
    
    def close_settings_dialog():
        """設定ダイアログを閉じる"""
        settings_dialog.open = False
        page.update()
    
    def save_settings():
        """設定を保存"""
        nonlocal preview_dir, main_app_dir
        
        new_preview_dir = preview_dir_textfield.value.strip()
        new_main_app_dir = main_app_dir_textfield.value.strip()
        
        # プレビューディレクトリの検証
        if new_preview_dir and not os.path.exists(new_preview_dir):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    f"プレビューフォルダーが見つかりません: {new_preview_dir}",
                    style=ft.TextStyle(font_family="Noto Sans CJK JP"),
                ),
                bgcolor=ft.Colors.RED,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # main.pyアプリのディレクトリの検証
        if new_main_app_dir and not os.path.exists(new_main_app_dir):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    f"main.pyアプリのフォルダーが見つかりません: {new_main_app_dir}",
                    style=ft.TextStyle(font_family="Noto Sans CJK JP"),
                ),
                bgcolor=ft.Colors.RED,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # main.pyアプリのsettings.jsonからpreview_dirを取得（設定されていない場合）
        if not new_preview_dir and new_main_app_dir:
            main_settings = get_settings_from_main_app(new_main_app_dir)
            if main_settings and "PREVIEW_DIR" in main_settings:
                new_preview_dir = resolve_preview_dir(main_settings["PREVIEW_DIR"], new_main_app_dir)
        
        preview_dir = new_preview_dir
        main_app_dir = new_main_app_dir
        
        # 設定を保存
        save_viewer_settings({
            "preview_dir": preview_dir,
            "main_app_dir": main_app_dir
        })
        
        # 監視を再起動
        if hasattr(page, 'observer') and page.observer:
            page.observer.stop()
            page.observer.join()
        
        if preview_dir and os.path.exists(preview_dir):
            start_watchdog(preview_dir)
        
        # 画像を更新
        update_images()
        
        close_settings_dialog()
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text(
                "設定を保存しました",
                style=ft.TextStyle(font_family="Noto Sans CJK JP"),
            ),
            bgcolor=ft.Colors.GREEN,
        )
        page.snack_bar.open = True
        page.update()
    
    def update_images():
        """画像を更新"""
        if not preview_dir or not os.path.exists(preview_dir):
            image1.src = ""
            image2.src = ""
            page.update()
            return
        
        image_files = get_latest_images(preview_dir, 2)
        
        if len(image_files) >= 2:
            # 2つの画像を横並びで表示
            image1.src = image_files[0]
            image2.src = image_files[1]
        elif len(image_files) == 1:
            # 1つの画像のみ
            image1.src = image_files[0]
            image2.src = ""
        else:
            # 画像なし
            image1.src = ""
            image2.src = ""
        
        page.update()
    
    def start_watchdog(watch_dir):
        """監視を開始"""
        if not watch_dir or not os.path.exists(watch_dir):
            return
        
        # 既存の監視を停止
        if hasattr(page, 'observer') and page.observer:
            try:
                page.observer.stop()
                page.observer.join()
            except:
                pass
        
        event_handler = ImageViewerHandler(page, watch_dir)
        observer = Observer()
        observer.schedule(event_handler, watch_dir, recursive=False)
        observer.start()
        page.observer = observer
    
    def terminate(event):
        """アプリケーションを終了"""
        if hasattr(page, 'observer') and page.observer:
            page.observer.stop()
            page.observer.join()
        page.window.close()
    
    # ページ設定
    page.title = "画像ビューア"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.maximized = True
    page.window.full_screen = True
    
    # メニューバー
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.IMAGE),
        leading_width=40,
        title=ft.Text("画像ビューア", size=12, style=ft.TextStyle(font_family="Noto Sans CJK JP")),
        center_title=False,
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        color=ft.Colors.BLACK,
        actions=[
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                tooltip="設定",
                on_click=open_settings_dialog,
            ),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="更新",
                on_click=lambda e: update_images(),
            ),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        text="設定",
                        on_click=open_settings_dialog,
                    ),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(
                        text="終了",
                        on_click=terminate,
                    ),
                ],
            ),
        ],
    )
    
    # メインレイアウト（2つの画像を横並び）
    main_layout = ft.Row(
        [image_container1, image_container2],
        spacing=0,
        expand=True,
    )
    
    page.add(main_layout)
    
    # 初期画像読み込み
    update_images()
    
    # 監視を開始
    if preview_dir and os.path.exists(preview_dir):
        start_watchdog(preview_dir)
    
    # 更新関数をページに保存
    page.update_images = update_images

# Fletアプリケーションを実行
if __name__ == "__main__":
    ft.app(target=main, view=ft.FLET_APP)
