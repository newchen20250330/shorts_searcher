@echo off
chcp 65001 >nul
echo ========================================
echo    YouTube Shorts Searcher - Install
echo    YouTube 短影片搜尋器 - 安裝程式
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo [錯誤] 未偵測到 Python
    echo.
    echo Please install Python 3.8 or newer
    echo 請先安裝 Python 3.8 或更新版本
    echo.
    echo Download: https://www.python.org/downloads/
    echo 下載網址: https://www.python.org/downloads/
    echo.
    echo Important: Check "Add Python to PATH" during installation
    echo 重要: 安裝時請勾選「Add Python to PATH」
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
echo [OK] 已偵測到 Python
python --version
echo.

REM Create virtual environment
echo [STEP 1] Creating virtual environment...
echo [步驟 1] 建立虛擬環境...
if exist .venv (
    echo [SKIP] Virtual environment already exists
    echo [跳過] 虛擬環境已存在
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo [錯誤] 建立虛擬環境失敗
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo [OK] 虛擬環境建立完成
)
echo.

REM Activate virtual environment and install packages
echo [STEP 2] Installing required packages...
echo [步驟 2] 安裝必要套件...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Package installation failed
    echo [錯誤] 套件安裝失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Installation completed!
echo [成功] 安裝完成！
echo ========================================
echo.
echo Next steps:
echo 下一步:
echo.
echo 1. Copy .env.example to .env
echo    複製 .env.example 為 .env
echo.
echo 2. Edit .env and add your YouTube API Key
echo    編輯 .env 檔案，填入你的 YouTube API Key
echo.
echo 3. Run "啟動.bat" to start the application
echo    雙擊「啟動.bat」執行程式
echo.
echo For API Key instructions, see "使用說明.txt"
echo API Key 取得方式請參考「使用說明.txt」
echo.
pause
