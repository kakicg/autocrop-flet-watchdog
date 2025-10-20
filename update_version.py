#!/usr/bin/env python3
import re
import os
import sys

def update_version():
    """バージョンファイルを更新する"""
    version_file = "version.py"
    
    # 現在のバージョンを読み取り
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            content = f.read()
            match = re.search(r'VERSION = "(\d+)\.(\d+)\.(\d+)"', content)
            if match:
                major, minor, patch = map(int, match.groups())
                patch += 1  # パッチバージョンを増加
            else:
                major, minor, patch = 1, 0, 0
    else:
        major, minor, patch = 1, 0, 0
    
    # 新しいバージョンでファイルを更新
    new_version = f'{major}.{minor}.{patch}'
    with open(version_file, 'w') as f:
        f.write(f'VERSION = "{new_version}"\n')
    
    print(f"バージョンを {new_version} に更新しました")
    return new_version

if __name__ == "__main__":
    update_version()
