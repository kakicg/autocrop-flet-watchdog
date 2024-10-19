import subprocess
import datetime
import time
import os

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

def download_and_delete_file(file_number, file_name, download_folder):
    """ファイルをダウンロードし、カメラから削除"""
    save_path = os.path.join(download_folder, file_name)
    subprocess.run(['gphoto2', '--get-file', str(file_number), '--filename', save_path])
    print(f"Downloaded: {file_name}")

    # カメラから削除
    subprocess.run(['gphoto2', '--delete-file', str(file_number)])
    print(f"Deleted from camera: {file_name}")

def monitor_camera(download_folder, interval=5):
    """新しいファイルが見つかるまで監視し、見つかったら終了してファイルリストを返す"""
    os.makedirs(download_folder, exist_ok=True)  # 保存先フォルダを作成

    previous_files = set(get_camera_files_with_timestamps())  # 初回ファイル一覧

    while True:
        time.sleep(interval)
        current_files = set(get_camera_files_with_timestamps())  # 最新のファイル一覧

        # 新しいファイルの検出
        new_files = current_files - previous_files
        if new_files:
            print("新しいファイルが見つかりました:")
            for file_number, file_name, timestamp in new_files:
                print(f"File: {file_name}, Timestamp: {timestamp}")
                download_and_delete_file(file_number, file_name, download_folder)

            # 見つかったファイルをリスト形式で返して終了
            return list(new_files)

        previous_files = current_files  # ファイル一覧を更新

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
            print(f"Found gvfsd-gphoto2 processes: {pids}")

            # 取得した全プロセスをkill
            for pid in pids:
                subprocess.run(['kill', '-9', pid])
                print(f"Killed process with PID: {pid}")
        else:
            print("No gvfsd-gphoto2 process found.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

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
    download_folder = "/path/to/download/folder"  # ダウンロード先を指定
    new_files = monitor_camera(download_folder)

    # ダウンロードされたファイルを使って次の処理に進む
    print("次の処理を開始します...")
    for file_number, file_name, timestamp in new_files:
        print(f"Processing: {file_name} (Timestamp: {timestamp})")
        # ここに加工や表示などの処理を追加
