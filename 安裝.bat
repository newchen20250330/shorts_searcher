@echo off
chcp 65001 >nul
echo ========================================
echo    YouTube 短影片搜尋器 - 安裝程式
echo ========================================
echo.

REM 檢查 Python 是否已安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未偵測到 Python
    echo.
    echo 請先安裝 Python 3.8 或更新版本
    echo 下載網址：https://www.python.org/downloads/
    echo.
    echo 安裝時請勾選「Add Python to PATH」
    echo.
    pause
    exit /b 1
)

echo ✅ 已偵測到 Python
python --version
echo.

REM 建立虛擬環境
echo 📦 建立虛擬環境...
if exist .venv (
    echo ⚠️  虛擬環境已存在，跳過建立
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 建立虛擬環境失敗
        pause
        exit /b 1
    )
    echo ✅ 虛擬環境建立完成
)
echo.

REM 啟動虛擬環境並安裝套件
echo 📥 安裝必要套件...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 套件安裝失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 安裝完成！
echo ========================================
echo.
echo 📝 下一步：
echo 1. 編輯 .env 檔案，填入你的 YouTube API Key
echo 2. 雙擊「啟動.bat」執行程式
echo.
echo 💡 如何取得 API Key？請參考「使用說明.txt」
echo.
pause
