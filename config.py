# グローバル定数設定ファイル

import json

PROCESSED_DIR = "./processed_images"
WATCH_DIR = "./watch_folder"

SETTINGS_PATH = "settings.json"

def load_settings():
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

def get_A():
    return load_settings()["A"]

def get_B():
    return load_settings()["B"]

def set_A_B(a, b):
    settings = load_settings()
    settings["A"] = a
    settings["B"] = b
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2) 