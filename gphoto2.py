import subprocess
import datetime
import os
from typing import List, Tuple

class Gphoto2:
    def __init__(self):
        super().__init__()

    def kill_gvfsd_gphoto2(self):
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'gvfsd-gphoto2'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-9', pid])
                    print(f"Killed process with PID: {pid}")
        
        except Exception as e:
            print(f"An error occurred: {e}")

    def call_kill_gvfsd_before(func):
        def wrapper(self, *args, **kwargs):
            # `self.kill_gvfsd_gphoto2()` を実行
            self.kill_gvfsd_gphoto2()
            return func(self, *args, **kwargs)
        return wrapper

    @call_kill_gvfsd_before
    def check_camera_connection(self) -> str:
        try:
            result = subprocess.run(
                ['gphoto2', '--auto-detect'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output = result.stdout.strip()
            if "No camera found" in output:
                return None
            else:
                return output
        
        except FileNotFoundError:
            print("gphoto2 is not installed. Please install it.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    @call_kill_gvfsd_before
    def capture_image(self):
        try:
            result = subprocess.run(
                ["gphoto2", "--capture-image-and-download", "--force-overwrite"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                file_name = "captured_image.jpg"
                return file_name
            else:
                print("カメラエラー:", result.stderr.decode())
                return None
        except Exception as e:
            print(f"カメラのエラー: {e}")
            return None
        
    @call_kill_gvfsd_before
    def capture_image_and_download(self, file_name: str, download_folder="./camera_images") -> str:
        """指定のファイル名とフォルダで画像をキャプチャしてダウンロードするメソッド"""
        try:
            # 保存先のパスを組み立て
            save_path = os.path.join(download_folder, file_name)
            
            # gphoto2を使って画像をキャプチャし、指定の場所にダウンロード
            result = subprocess.run(
                ["gphoto2", "--capture-image-and-download", "--filename", save_path, "--force-overwrite"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # コマンドの実行結果の確認
            if result.returncode == 0:
                print(f"Captured and downloaded image to: {save_path}")
                return save_path
            else:
                print("カメラエラー:", result.stderr.strip())
                return None

        except Exception as e:
            print(f"カメラのエラー: {e}")
            return None

    @call_kill_gvfsd_before
    def get_camera_files_with_timestamps(self) -> List[Tuple[int, str, datetime.datetime]]:
        try:
            result = subprocess.run(['gphoto2', '--list-files'], stdout=subprocess.PIPE, text=True)
            files_with_timestamps = []

            for line in result.stdout.splitlines():
                if line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 5:
                        file_name = parts[1]
                        file_number = int(parts[0][1:])
                        timestamp = int(parts[-1])
                        dt_object = datetime.datetime.fromtimestamp(timestamp)
                        files_with_timestamps.append((file_number, file_name, dt_object))

            return files_with_timestamps
        except subprocess.CalledProcessError as e:
            print(f"コマンドがエラー終了しました (コード: {e.returncode})")
            print(f"{e.stderr.strip()}")
        except FileNotFoundError:
            print("gphoto2が見つかりません。インストールされていることを確認してください。")

    @call_kill_gvfsd_before
    def delete_all_files(self):
        try:
            result = subprocess.run(
                ['gphoto2', '--delete-all-files', '--recurse'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                print("All files deleted successfully.")
                print(result.stdout)
            else:
                print("Failed to delete files.")
                print(result.stderr)
        except FileNotFoundError:
            print("gphoto2 is not installed. Please install it.")
        except Exception as e:
            print(f"An error occurred: {e}")

    @call_kill_gvfsd_before
    def download_file(self, file_number, file_name, download_folder="./camera_images"):
        save_path = os.path.join(download_folder, file_name)
        subprocess.run(['gphoto2', '--get-file', str(file_number), '--filename', save_path])
        print(f"Downloaded: {file_name}")

gp2 = Gphoto2()
def list_files(results):
    if len(results) == 0:
        print("No File")
        return
    for res in results:
        print(res)

if __name__ == "__main__":
    # result = gp2.check_camera_connection()
    # if result:
    #     print(result)
    # else:
    #     print("カメラ認識できません")

    # gp2.capture_image()

    # list_files(gp2.get_camera_files_with_timestamps())

    # gp2.download_file(1, "test.jpg", "./test_images")
    # gp2.delete_all_files()

    # list_files(gp2.get_camera_files_with_timestamps())
    gp2.capture_image_and_download("capture_test.jpg")

    
    