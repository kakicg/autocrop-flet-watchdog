# グローバル定数設定ファイル

import json
import os
import sys
from datetime import datetime

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
        
        # マージン項目がない場合はデフォルト値5%（パーセント）を追加
        if "MARGIN_TOP" not in settings:
            settings["MARGIN_TOP"] = 5.0
            updated = True
        if "MARGIN_BOTTOM" not in settings:
            settings["MARGIN_BOTTOM"] = 5.0
            updated = True
        if "MARGIN_LEFT" not in settings:
            settings["MARGIN_LEFT"] = 5.0
            updated = True
        if "MARGIN_RIGHT" not in settings:
            settings["MARGIN_RIGHT"] = 5.0
            updated = True
        
        # 累計撮影枚数と起算日がない場合は初期化
        if "TOTAL_SHOTS" not in settings:
            settings["TOTAL_SHOTS"] = 0
            updated = True
        if "SHOT_COUNT_START_DATE" not in settings:
            settings["SHOT_COUNT_START_DATE"] = datetime.now().strftime("%Y-%m-%d")
            updated = True
        
        # 縦横比設定がない場合はデフォルト値"4:3"を追加
        if "ASPECT_RATIO" not in settings:
            settings["ASPECT_RATIO"] = "4:3"
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

def get_MARGIN_TOP():
    """上マージンを取得（パーセント）"""
    settings = load_settings()
    if "MARGIN_TOP" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("MARGIN_TOP", 5.0)

def get_MARGIN_BOTTOM():
    """下マージンを取得（パーセント）"""
    settings = load_settings()
    if "MARGIN_BOTTOM" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("MARGIN_BOTTOM", 5.0)

def get_MARGIN_LEFT():
    """左マージンを取得（パーセント）"""
    settings = load_settings()
    if "MARGIN_LEFT" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("MARGIN_LEFT", 5.0)

def get_MARGIN_RIGHT():
    """右マージンを取得（パーセント）"""
    settings = load_settings()
    if "MARGIN_RIGHT" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("MARGIN_RIGHT", 5.0)

def set_MARGIN_TOP(value):
    """上マージンを設定（パーセント）"""
    settings = load_settings()
    settings["MARGIN_TOP"] = float(value)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def set_MARGIN_BOTTOM(value):
    """下マージンを設定（パーセント）"""
    settings = load_settings()
    settings["MARGIN_BOTTOM"] = float(value)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def set_MARGIN_LEFT(value):
    """左マージンを設定（パーセント）"""
    settings = load_settings()
    settings["MARGIN_LEFT"] = float(value)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def set_MARGIN_RIGHT(value):
    """右マージンを設定（パーセント）"""
    settings = load_settings()
    settings["MARGIN_RIGHT"] = float(value)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def get_TOTAL_SHOTS():
    """累計撮影枚数を取得"""
    settings = load_settings()
    if "TOTAL_SHOTS" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("TOTAL_SHOTS", 0)

def increment_TOTAL_SHOTS():
    """累計撮影枚数を1つ増やす"""
    settings = load_settings()
    # 初めて呼び出された場合は起算日を設定
    if "TOTAL_SHOTS" not in settings or "SHOT_COUNT_START_DATE" not in settings:
        settings["TOTAL_SHOTS"] = 0
        settings["SHOT_COUNT_START_DATE"] = datetime.now().strftime("%Y-%m-%d")
    settings["TOTAL_SHOTS"] = settings.get("TOTAL_SHOTS", 0) + 1
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def reset_TOTAL_SHOTS():
    """累計撮影枚数をリセットして0に戻し、起算日を更新"""
    settings = load_settings()
    settings["TOTAL_SHOTS"] = 0
    settings["SHOT_COUNT_START_DATE"] = datetime.now().strftime("%Y-%m-%d")
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def get_SHOT_COUNT_START_DATE():
    """起算日を取得"""
    settings = load_settings()
    if "SHOT_COUNT_START_DATE" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("SHOT_COUNT_START_DATE", datetime.now().strftime("%Y-%m-%d"))

def get_ASPECT_RATIO():
    """縦横比を取得（"4:3"、"3:2"または"1:1"）"""
    settings = load_settings()
    if "ASPECT_RATIO" not in settings:
        initialize_settings()
        settings = load_settings()
    return settings.get("ASPECT_RATIO", "4:3")

def set_ASPECT_RATIO(ratio):
    """縦横比を設定（"4:3"、"3:2"または"1:1"）"""
    if ratio not in ["4:3", "3:2", "1:1"]:
        raise ValueError("縦横比は'4:3'、'3:2'または'1:1'である必要があります")
    settings = load_settings()
    settings["ASPECT_RATIO"] = ratio
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2) 