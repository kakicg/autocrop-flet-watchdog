import sys
from cx_Freeze import setup, Executable

# 依存関係を含める
build_exe_options = {
    "packages": ["flet", "sqlalchemy", "watchdog", "cv2", "numpy"],
    "include_files": [
        "product_data.db",
        "settings.json", 
        "preview/",
        "processed/",
        "watch_folder/",
        "storage/",
        "barcode.jpg"
    ],
    "excludes": ["tkinter", "unittest", "pydoc", "difflib"]
}

# 実行ファイルの設定
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # GUIアプリケーションとして実行

setup(
    name="AutoCrop",
    version="1.0",
    description="商品撮影システム",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="AutoCrop.exe")]
)
