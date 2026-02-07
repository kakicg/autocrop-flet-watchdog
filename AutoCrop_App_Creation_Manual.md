# AutoCrop デスクトップアプリ作成マニュアル

## 概要
このマニュアルでは、AutoCropアプリケーションをPyInstallerを使用してデスクトップアプリとして作成する手順を説明します。

## 前提条件

### 必要なソフトウェア
- Python 3.12以上
- PyInstaller
- Flet
- SQLAlchemy
- OpenCV-Python
- Watchdog

### 必要なライブラリのインストール
```bash
pip install flet sqlalchemy opencv-python watchdog pyinstaller
```

## 手順

### 1. 環境の準備
```bash
# 現在のディレクトリを確認
pwd

# 必要なファイルが存在することを確認
ls main.py
ls config.py
ls sidebar.py
ls watchdog_process.py
ls product_data.db
ls settings.json
```

### 2. 既存のビルドファイルのクリーンアップ
```bash
# 既存のdistとbuildフォルダを削除
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
```

### 3. PyInstallerでのビルド
```bash
python -m PyInstaller --name "AutoCrop" --onedir --windowed --add-data "product_data.db;." --add-data "settings.json;." --add-data "preview;preview" --add-data "processed;processed" --add-data "watch_folder;watch_folder" --add-data "storage;storage" --add-data "barcode.jpg;." --hidden-import flet --hidden-import sqlalchemy --hidden-import watchdog --hidden-import cv2 --hidden-import numpy --collect-all flet --collect-all sqlalchemy --collect-all watchdog main.py --clean -y
```

### 4. Windowsセキュリティブロックの解除
```bash
cd dist\AutoCrop
Unblock-File .\AutoCrop.exe
```

### 5. アプリケーションのテスト
```bash
.\AutoCrop.exe
```

## 重要なポイント

### config.pyの修正
PyInstaller環境でファイルパスを正しく解決するために、`config.py`に以下のコードが必要です：

```python
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
```

### PyInstallerコマンドのオプション説明
- `--name "AutoCrop"`: 実行ファイル名を指定
- `--onedir`: 単一ディレクトリにすべてのファイルを含める
- `--windowed`: GUIアプリケーションとして実行（コンソールウィンドウなし）
- `--add-data "ファイル;."`: データファイルをアプリに含める
- `--hidden-import`: 明示的にインポートするモジュールを指定
- `--collect-all`: 指定したパッケージのすべてのモジュールを収集
- `--clean`: ビルド前にキャッシュをクリア
- `-y`: 確認なしで既存ファイルを上書き

## トラブルシューティング

### よくある問題と解決方法

#### 1. "No module named 'flet'" エラー
**原因**: Fletがインストールされていない
**解決方法**: 
```bash
pip install flet
```

#### 2. "settings.json not found" エラー
**原因**: config.pyがPyInstaller環境に対応していない
**解決方法**: config.pyを上記のコードに修正

#### 3. "AutoCrop.exe not found" エラー
**原因**: Windowsセキュリティがファイルをブロックしている
**解決方法**: 
```bash
Unblock-File .\AutoCrop.exe
```

#### 4. 依存関係の不足
**原因**: 必要なライブラリがインストールされていない
**解決方法**: 
```bash
pip install -r requirements.txt
```

## 配布方法

### 配布用ファイルの準備
1. `dist\AutoCrop`フォルダ全体をコピー
2. 受信者に配布

### 受信者側での実行
1. `AutoCrop.exe`をダブルクリック
2. Windowsセキュリティの警告が出た場合は「詳細情報」→「実行」をクリック

## ファイル構成

### 作成されるファイル
```
dist\AutoCrop\
├── AutoCrop.exe          # メイン実行ファイル
├── _internal\            # 依存関係とライブラリ
│   ├── flet\            # Fletライブラリ
│   ├── sqlalchemy\      # SQLAlchemyライブラリ
│   ├── watchdog\        # Watchdogライブラリ
│   ├── cv2\             # OpenCVライブラリ
│   ├── numpy\           # NumPyライブラリ
│   ├── settings.json    # 設定ファイル
│   ├── product_data.db  # データベースファイル
│   ├── preview\         # プレビュー画像フォルダ
│   ├── processed\       # 処理済み画像フォルダ
│   ├── watch_folder\    # 監視フォルダ
│   └── storage\         # ストレージフォルダ
└── barcode.jpg          # バーコード画像
```

## 更新手順

### アプリケーションの更新
1. ソースコードを修正
2. 上記の手順1-5を実行
3. 新しい`dist\AutoCrop`フォルダを配布

### 設定ファイルの更新
1. `settings.json`を修正
2. `dist\AutoCrop\_internal\settings.json`を更新
3. 必要に応じて`dist\AutoCrop\settings.json`も更新

## 注意事項

- Python環境は3.12以上を使用
- ビルド前に必ず既存のdistとbuildフォルダを削除
- Windowsセキュリティブロックを必ず解除
- 配布時は`dist\AutoCrop`フォルダ全体をコピー
- 受信者側ではPythonのインストールは不要

## 参考情報

- PyInstaller公式ドキュメント: https://pyinstaller.readthedocs.io/
- Flet公式ドキュメント: https://flet.dev/
- このマニュアルは2025年10月22日時点の情報に基づいています












