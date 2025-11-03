# グローバル定数設定ファイル

import json
import os
import sys

def get_settings_path():
    """PyInstaller環境でも正しくsettings.jsonを見つける"""
    if getattr(sys, 'frozen', False):
        # PyInstaller環境の場合
        base_path = sys._MEIPASS
        settings_path = os.path.join(base_path, "settings.json")
        if os.path.exists(settings_path):
            return settings_path
        # メインディレクトリも確認
        main_dir = os.path.dirname(sys.executable)
        settings_path = os.path.join(main_dir, "settings.json")
        if os.path.exists(settings_path):
            return settings_path
    # 通常のPython環境の場合
    return "settings.json"

SETTINGS_PATH = get_settings_path()

def load_settings():
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

def get_A():
    return load_settings()["A"]

def get_B():
    return load_settings()["B"]

def get_PROCESSED_DIR():
    return load_settings()["PROCESSED_DIR"]

def get_WATCH_DIR():
    return load_settings()["WATCH_DIR"]

def get_PREVIEW_DIR():
    """プレビューフォルダーのパスを取得"""
    settings = load_settings()
    # 念のため、まだPREVIEW_DIRがない場合は初期化を試みる
    if "PREVIEW_DIR" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("PREVIEW_DIR", "preview")

def initialize_settings():
    """アプリケーション起動時に設定を初期化。新しい項目があれば追加"""
    try:
        settings = load_settings()
        updated = False
        
        # GAMMA項目がない場合はデフォルト値3.0を追加
        if "GAMMA" not in settings:
            settings["GAMMA"] = 3.0
            updated = True
        
        # PREVIEW_DIR項目がない場合はデフォルト値"preview"を追加
        if "PREVIEW_DIR" not in settings:
            settings["PREVIEW_DIR"] = "preview"
            updated = True
        
        # 設定が更新された場合はファイルに保存
        if updated:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"設定の初期化エラー: {e}")

def get_GAMMA():
    """ガンマ値を取得"""
    settings = load_settings()
    # 念のため、まだGAMMAがない場合は初期化を試みる
    if "GAMMA" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("GAMMA", 3.0)

def set_A_B(a, b):
    settings = load_settings()
    settings["A"] = a
    settings["B"] = b
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def set_PROCESSED_DIR(path):
    settings = load_settings()
    settings["PROCESSED_DIR"] = path
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def set_WATCH_DIR(path):
    settings = load_settings()
    settings["WATCH_DIR"] = path
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def set_GAMMA(gamma):
    """ガンマ値を設定"""
    settings = load_settings()
    settings["GAMMA"] = gamma
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def set_PREVIEW_DIR(path):
    """プレビューフォルダーのパスを設定"""
    settings = load_settings()
    settings["PREVIEW_DIR"] = path
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2) 