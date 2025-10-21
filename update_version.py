#!/usr/bin/env python3
import re
import os
import sys
import subprocess

def determine_version_bump(commit_message):
    """コミットメッセージからバージョン増加タイプを判定"""
    commit_lower = commit_message.lower()
    
    # メジャーバージョン
    if any(keyword in commit_lower for keyword in [
        'major', 'breaking', 'incompatible', 'remove', 'delete', '破壊的変更'
    ]):
        return "major"
    
    # マイナーバージョン
    elif any(keyword in commit_lower for keyword in [
        '機能追加', '改善', 'feature', 'add', 'new', 'enhancement', 'improve'
    ]):
        return "minor"
    
    # パッチバージョン（デフォルト）
    else:
        return "patch"

def get_latest_commit_message():
    """最新のコミットメッセージを取得"""
    try:
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return ""

def update_version(change_type=None):
    """バージョンファイルを更新する"""
    version_file = "version.py"
    
    # 現在のバージョンを読み取り
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            content = f.read()
            match = re.search(r'VERSION = "(\d+)\.(\d+)\.(\d+)"', content)
            if match:
                major, minor, patch = map(int, match.groups())
            else:
                major, minor, patch = 1, 0, 0
    else:
        major, minor, patch = 1, 0, 0
    
    # バージョン増加タイプを決定
    if change_type is None:
        commit_message = get_latest_commit_message()
        change_type = determine_version_bump(commit_message)
    
    # バージョンを増加
    if change_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif change_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    # 新しいバージョンでファイルを更新
    new_version = f'{major}.{minor}.{patch}'
    with open(version_file, 'w') as f:
        f.write(f'VERSION = "{new_version}"\n')
    
    print(f"バージョンを {new_version} に更新しました ({change_type})")
    return new_version

if __name__ == "__main__":
    # コマンドライン引数で手動指定も可能
    change_type = None
    if len(sys.argv) > 1:
        change_type = sys.argv[1]  # major, minor, patch
    
    update_version(change_type)
