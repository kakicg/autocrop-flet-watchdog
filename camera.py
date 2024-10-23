import subprocess
import datetime
import time
import os
import flet as ft

def kill_gvfsd_gphoto2():
    try:
        # gvfsd-gphoto2 のプロセスを探す
        result = subprocess.run(
            ['pgrep', '-f', 'gvfsd-gphoto2'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.stdout:
            # プロセスIDを取得し、表示
            pids = result.stdout.strip().split('\n')
            # print(f"Found gvfsd-gphoto2 processes: {pids}")

            # 取得した全プロセスをkill
            for pid in pids:
                subprocess.run(['kill', '-9', pid])
                print(f"Killed process with PID: {pid}")
        # else:
        #     print("No gvfsd-gphoto2 process found.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

def call_kill_gvfsd_before(kill_gvfsd_gphoto2):
    def decorator(funcB):
        def wrapper(*args, **kwargs):
            # funcBの冒頭でfuncAを実行
            kill_gvfsd_gphoto2()
            # 続いてfuncBを実行
            return funcB(*args, **kwargs)
        return wrapper
    return decorator

@call_kill_gvfsd_before(kill_gvfsd_gphoto2)
def get_camera_files_with_timestamps():
    """カメラ内のファイル名とタイムスタンプのペアを取得する関数"""
    result = subprocess.run(['gphoto2', '--list-files'], stdout=subprocess.PIPE, text=True)
    files_with_timestamps = []

    for line in result.stdout.splitlines():
        if line.startswith('#'):  # ファイル情報行を取得
            parts = line.split()
            if len(parts) >= 5:
                file_name = parts[1]  # ファイル名
                file_number = int(parts[0][1:])  # "#1"の形式から番号を取得
                timestamp = int(parts[-1])  # Unixタイムスタンプ
                dt_object = datetime.datetime.fromtimestamp(timestamp)  # 日時形式に変換
                files_with_timestamps.append((file_number, file_name, dt_object))

    return files_with_timestamps

@call_kill_gvfsd_before(kill_gvfsd_gphoto2)
def delete_all_files():
    """gphoto2で全ファイルを再帰的に削除する関数"""
    try:
        # gphoto2コマンドの実行
        result = subprocess.run(
            ['gphoto2', '--delete-all-files', '--recurse'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # コマンド実行結果の確認
        if result.returncode == 0:
            print("All files deleted successfully.")
            print(result.stdout)  # 実行結果の標準出力を表示
        else:
            print("Failed to delete files.")
            print(result.stderr)  # エラー内容を表示

    except FileNotFoundError:
        print("gphoto2 is not installed. Please install it.")
    except Exception as e:
        print(f"An error occurred: {e}")

@call_kill_gvfsd_before(kill_gvfsd_gphoto2)
def download_file(file_number, file_name, download_folder):
    """ファイルをダウンロードし、カメラから削除"""
    save_path = os.path.join(download_folder, file_name)
    subprocess.run(['gphoto2', '--get-file', str(file_number), '--filename', save_path])
    print(f"Downloaded: {file_name}")

@call_kill_gvfsd_before(kill_gvfsd_gphoto2)
def monitor_camera(page:ft.Page = None ,download_folder="./camera_images", interval=0.5):
    delete_all_files()  # ループに入る前にカメラ内の全ファイルを削除
    """新しいファイルが見つかるまで監視し、見つかったら終了してファイルリストを返す"""
    os.makedirs(download_folder, exist_ok=True)  # 保存先フォルダを作成
    i=0
    while True:
        print(i)
        i+=1
        if page and not page.session.get("camera_loop"):
            break
        time.sleep(interval)
        new_files = get_camera_files_with_timestamps()
        # 新しいファイルの検出
        if new_files:
            print("新しいファイルが見つかりました:")
            result_list = []  # 新しいファイルをリストとして管理

            for file_number, file_name, timestamp in new_files:
                print(f"File: {file_name}, Timestamp: {timestamp}")
                download_file(file_number, file_name, download_folder)
                result_list.append(file_name)

            # 見つかったファイルをリスト形式で返して終了
            delete_all_files()  # ダウンロード後にカメラ内のファイルを削除
            if result_list:
                return result_list[-1]
            return ""
    return ""


@call_kill_gvfsd_before(kill_gvfsd_gphoto2)
def capture_image():
    try:
        # GPhoto2を使用して画像をキャプチャしてダウンロード
        result = subprocess.run(
            ["gphoto2", "--capture-image-and-download", "--force-overwrite"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            # 新しい画像ファイル名を取得（例としてファイル名を固定）
            file_name = "captured_image.jpg"
            return file_name
        else:
            print("カメラエラー:", result.stderr.decode())
            return None
    except Exception as e:
        print(f"カメラのエラー: {e}")
        return None
    
@call_kill_gvfsd_before(kill_gvfsd_gphoto2)
def check_camera_connection():
    try:
        # gphoto2 --auto-detect コマンドの実行
        result = subprocess.run(
            ['gphoto2', '--auto-detect'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 出力結果の処理
        output = result.stdout.strip()
        if "No camera found" in output:
            print("No camera detected.")
        else:
            print("Camera detected:")
            print(output)
    
    except FileNotFoundError:
        print("gphoto2 is not installed. Please install it using Homebrew: 'brew install gphoto2'.")
    except Exception as e:
        print(f"An error occurred: {e}")

# 呼び出し元からの使い方例
if __name__ == '__main__':
    download_folder = "./camera_images"  # ダウンロード先を指定
    file_name = monitor_camera(download_folder=download_folder, interval=3)

    # ダウンロードされたファイルを使って次の処理に進む
    print(f"Processing: {file_name}")
