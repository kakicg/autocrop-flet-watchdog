"""
外部アプリケーションを起動するためのユーティリティモジュール
"""
import subprocess
import os
import sys
import platform


def launch_app(app_path: str, args: list = None) -> subprocess.Popen:
    """
    外部アプリケーションを起動する
    
    Args:
        app_path: アプリケーションのパス
            - macOS: .app形式のパス（例: "/Applications/MyApp.app"）
            - Windows: .exe形式のパス（例: "C:\\Program Files\\MyApp\\MyApp.exe"）
            - Linux: 実行可能ファイルのパス（例: "/usr/bin/myapp"）
        args: アプリケーションに渡す引数のリスト（オプション）
    
    Returns:
        subprocess.Popen: 起動したプロセスのオブジェクト
    
    Raises:
        FileNotFoundError: アプリケーションが見つからない場合
        subprocess.SubprocessError: 起動に失敗した場合
    """
    if args is None:
        args = []
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # .app形式のアプリケーションを起動
        if app_path.endswith('.app'):
            # macOSでは.app内の実行可能ファイルを起動
            executable_path = os.path.join(app_path, "Contents", "MacOS")
            # 実行可能ファイル名を取得（通常は.app名と同じ）
            app_name = os.path.basename(app_path).replace('.app', '')
            executable = os.path.join(executable_path, app_name)
            
            if not os.path.exists(executable):
                # 別の方法: openコマンドを使用
                cmd = ["open", "-a", app_path]
                if args:
                    cmd.extend(["--args"] + args)
                return subprocess.Popen(cmd)
            else:
                # 実行可能ファイルを直接起動
                return subprocess.Popen([executable] + args)
        else:
            # 通常の実行可能ファイル
            return subprocess.Popen([app_path] + args)
    
    elif system == "Windows":
        # Windowsの場合
        if app_path.endswith('.exe'):
            return subprocess.Popen([app_path] + args)
        else:
            # .exe以外も起動可能
            return subprocess.Popen([app_path] + args)
    
    else:  # Linux
        # Linuxの場合
        return subprocess.Popen([app_path] + args)


def launch_app_detached(app_path: str, args: list = None) -> None:
    """
    外部アプリケーションを分離プロセスとして起動（親プロセスが終了しても子プロセスは継続）
    
    Args:
        app_path: アプリケーションのパス
        args: アプリケーションに渡す引数のリスト（オプション）
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        if app_path.endswith('.app'):
            cmd = ["open", "-a", app_path]
            if args:
                cmd.extend(["--args"] + args)
            # 分離プロセスとして起動
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                            start_new_session=True)
        else:
            subprocess.Popen([app_path] + (args or []), 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           start_new_session=True)
    
    elif system == "Windows":
        # WindowsではCREATE_NEW_PROCESS_GROUPを使用
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        subprocess.Popen([app_path] + (args or []), 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=creation_flags)
    
    else:  # Linux
        subprocess.Popen([app_path] + (args or []), 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        start_new_session=True)


def check_app_exists(app_path: str) -> bool:
    """
    アプリケーションが存在するかチェック
    
    Args:
        app_path: アプリケーションのパス
    
    Returns:
        bool: アプリケーションが存在する場合True
    """
    system = platform.system()
    
    if system == "Darwin" and app_path.endswith('.app'):
        # macOSの.app形式の場合
        executable_path = os.path.join(app_path, "Contents", "MacOS")
        app_name = os.path.basename(app_path).replace('.app', '')
        executable = os.path.join(executable_path, app_name)
        return os.path.exists(app_path) or os.path.exists(executable)
    
    return os.path.exists(app_path)


# 使用例
if __name__ == "__main__":
    # 例: 同じプロジェクト内のdist/AutoCrop.appを起動
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "dist", "AutoCrop.app")
    
    if check_app_exists(app_path):
        print(f"アプリを起動します: {app_path}")
        try:
            process = launch_app(app_path)
            print(f"アプリが起動しました。プロセスID: {process.pid}")
        except Exception as e:
            print(f"アプリの起動に失敗しました: {e}")
    else:
        print(f"アプリが見つかりません: {app_path}")


