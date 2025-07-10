# グローバル定数設定ファイル

import json

SETTINGS_PATH = "settings.json"

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