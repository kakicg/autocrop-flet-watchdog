import subprocess
import time

def get_camera_files():
    """GPhoto2を使ってカメラ内のファイル一覧を取得する関数"""
    result = subprocess.run(['gphoto2', '--list-files'], stdout=subprocess.PIPE, text=True)
    files = []
    for line in result.stdout.splitlines():
        if line.startswith('#'):
            parts = line.split()
            if len(parts) > 1:
                file_path = parts[1]
                files.append(file_path)
    return set(files)

def monitor_camera(interval=0.5):
    """カメラ内の新しい画像ファイルを監視する関数"""
    previous_files = get_camera_files()
    while True:
        time.sleep(interval)
        current_files = get_camera_files()
        new_files = current_files - previous_files
        if new_files:
            print(f"新しい画像ファイルが見つかりました: {new_files}")
            # 新しいファイルの処理をここで行う
        previous_files = current_files


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

if __name__ == "__main__":
    check_camera_connection()
    monitor_camera()