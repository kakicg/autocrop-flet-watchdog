@echo off
chcp 65001 >nul
echo AutoCrop Desktop App Build (flet pack - single exe in dist)
echo ==========================================

echo.
echo 1. Cleaning old build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo Done.

echo.
echo 1b. Finding flet and ensuring PyInstaller for same Python...
set "FLET_EXE="
set "PY_FOR_PACK=python"
for /f "delims=" %%e in ('python -c "import sys, os; p=os.path.join(os.path.dirname(sys.executable), 'Scripts', 'flet.exe'); print(p)" 2^>nul') do set "FLET_EXE=%%e"
if not defined FLET_EXE for /f "tokens=1,2" %%a in ('python -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2^>nul') do set "FLET_EXE=%APPDATA%\Python\Python%%a%%b\Scripts\flet.exe"
if defined FLET_EXE if exist "%FLET_EXE%" (
    echo Using flet from: %FLET_EXE%
    set "PY_FOR_PACK=python"
    if exist "%ProgramFiles%\Python312\python.exe" set "PY_FOR_PACK=%ProgramFiles%\Python312\python.exe"
    if exist "%ProgramFiles(x86)%\Python312\python.exe" if "%PY_FOR_PACK%"=="python" set "PY_FOR_PACK=%ProgramFiles(x86)%\Python312\python.exe"
)
"%PY_FOR_PACK%" -m pip install pyinstaller -q
echo Done.

echo.
echo 2. Building with flet pack...
if defined FLET_EXE if exist "%FLET_EXE%" (
    "%FLET_EXE%" pack main.py --name "AutoCrop" --icon autocrop.ico -y --hidden-import pico_led --hidden-import serial --hidden-import serial.tools.list_ports
) else (
    flet pack main.py --name "AutoCrop" --icon autocrop.ico -y --hidden-import pico_led --hidden-import serial --hidden-import serial.tools.list_ports
)

if %ERRORLEVEL% neq 0 (
    echo Build failed. Check errors above.
    pause
    exit /b 1
)

echo.
echo 3. Unblocking executable...
if exist dist\AutoCrop.exe powershell -Command "Unblock-File -Path 'dist\AutoCrop.exe'"

echo.
echo 4. Build complete.
echo Output: dist\AutoCrop.exe
echo.
set /p choice=Run app now? (Y/N): 
if /i "%choice%"=="Y" (
    echo Starting...
    start "" "dist\AutoCrop.exe"
)

echo.
echo Done.
pause
