@echo off
echo ============================================
echo   MarkdownReader - Portable EXE Builder
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [2/4] Cleaning previous build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [3/4] Building portable EXE (this may take a few minutes)...
pyinstaller MarkdownReader.spec --noconfirm --clean
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo [4/4] Build complete!
echo.
echo ============================================
echo   Output: dist\MarkdownReader\MarkdownReader.exe
echo ============================================
echo.

REM Open the output folder
explorer dist\MarkdownReader

pause
