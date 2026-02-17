@echo off
setlocal
set HOOK_SRC=%~dp0githooks\prepare-commit-msg
set HOOK_DST=%~dp0.git\hooks\prepare-commit-msg
if not exist "%~dp0.git\hooks" (
  echo .git/hooks が見つかりません。リポジトリのルートで実行してください。
  exit /b 1
)
copy /Y "%HOOK_SRC%" "%HOOK_DST%" >nul
echo prepare-commit-msg フックをインストールしました。
echo これ以降、commit するたびに version.py が自動で上がります。
endlocal
