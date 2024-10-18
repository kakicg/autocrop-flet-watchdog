import asyncio
import time
import os
from camera import capture_image
from barcode_reader import read_barcode
from image_processing import process_image
from gui import start_gui, update_gui
import flet as ft
import random

# グローバル設定
a = 1.0  # 高さ計算の係数a
b = 10.0  # 高さ計算の係数b
capture_count = 5  # 繰り返し撮影回数
gui_test = True

test_image_folder = "./test_processed_images"  # テスト用画像フォルダ
processed_images_folder = "./processed_images"  # 処理済み画像フォルダ

async def process_and_show_image(image_path, height, page):
    """非同期で画像を処理し、GUIを更新する"""
    # 非同期処理として少し待つ（例：画像処理のシミュレーション）
    await asyncio.sleep(0.1)
    
    # GUIの更新をメインスレッドで実行
    await update_gui(page, image_path, height)

async def main_loop(page, controls):
    test_images = sorted(os.listdir(test_image_folder))  # フォルダ内の画像を取得し、ソート
    image_index = 0

    while True:
        if not gui_test:
            # バーコードを読み取る
            product_id = read_barcode()
        else:
            # キーボードからバーコードを入力
            random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            product_id = random_digits

        # n回撮影処理を行う
        for n in range(1, capture_count + 1):
            if not gui_test:
                # カメラで撮影する
                file_path = capture_image()

                if file_path:
                    # OpenCVで画像処理を行い、高さを推定する
                    processed_image, height = process_image(file_path, a, b)

                    # 画像を保存する
                    output_file = f"{product_id}_{n}.jpg"
                    processed_image.save(output_file)

                else:
                    print("カメラ画像が見つかりません。")

            else: #テストモード
                if image_index < len(test_images):
                    output_file = os.path.join(test_image_folder, test_images[image_index])
                    print(f"output_file: {output_file}")
                    height = random.randint(100, 300)

                    image_index += 1
                else:
                    print("テスト用画像がなくなりました。")
                    return

            # 非同期で画像を処理して表示する
            await process_and_show_image(output_file, height, page)

        # ループ終了確認
        if not continue_loop() or gui_test:
            break

def continue_loop():
    # GUIのプルダウンで「終了」が選択されたらFalseを返す
    return True  # 仮実装。GUIからの入力処理に変更する必要があります。

def main(page: ft.Page):
    page.title = "製品撮影システム"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 50
    page.update()

    images = ft.GridView(
        expand=1,
        runs_count=5,
        max_extent=200,
        child_aspect_ratio=0.5625,
        spacing=15,
        run_spacing=15,
    )
    processed_images = os.listdir(processed_images_folder)  # フォルダ内の画像を取得し、ソト
    for image_path in processed_images:

        images.controls.insert(0,
            ft.Column(
                [
                    ft.Image(
                    src=image_path,
                    fit=ft.ImageFit.COVER,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    # border_radius=ft.border_radius.all(10),
                    ),
                    ft.Text(
                        f"Name:{image_path}",
                        size=10,
                        color=ft.colors.WHITE,
                        weight=ft.FontWeight.W_100,
                    ),
                ]
            )  
        )
    
    page.add(images)

    page.update()
    # 非同期のメインループを実行
    asyncio.run(main_loop(page,images.controls))

if __name__ == "__main__":
    ft.app(target=main)