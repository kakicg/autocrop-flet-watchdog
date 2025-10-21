@echo off
echo AutoCrop デスクトップアプリ作成スクリプト
echo ==========================================

echo.
echo 1. 既存のビルドファイルをクリーンアップ中...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo クリーンアップ完了

echo.
echo 2. PyInstallerでアプリをビルド中...
python -m PyInstaller --name "AutoCrop" --onedir --windowed --add-data "product_data.db;." --add-data "settings.json;." --add-data "preview;preview" --add-data "processed;processed" --add-data "watch_folder;watch_folder" --add-data "storage;storage" --add-data "barcode.jpg;." --hidden-import flet --hidden-import sqlalchemy --hidden-import watchdog --hidden-import cv2 --hidden-import numpy --collect-all flet --collect-all sqlalchemy --collect-all watchdog main.py --clean -y

if %ERRORLEVEL% neq 0 (
    echo ビルドに失敗しました。エラーを確認してください。
    pause
    exit /b 1
)

echo.
echo 3. Windowsセキュリティブロックを解除中...
cd dist\AutoCrop
powershell -Command "Unblock-File .\AutoCrop.exe"

echo.
echo 4. ビルド完了！
echo 実行ファイル: dist\AutoCrop\AutoCrop.exe
echo.
echo アプリをテストしますか？ (Y/N)
set /p choice=
if /i "%choice%"=="Y" (
    echo アプリを起動中...
    .\AutoCrop.exe
)

echo.
echo 完了！
pause


