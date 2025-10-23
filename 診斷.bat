@echo off
chcp 65001 >nul
echo ========================================
echo    Diagnostic Tool - System Check
echo    診斷工具 - 系統檢查
echo ========================================
echo.

echo [CHECK 1] Python Version
echo [檢查 1] Python 版本
python --version
echo.

echo [CHECK 2] Python Executable Path
echo [檢查 2] Python 執行檔路徑
python -c "import sys; print(sys.executable)"
echo.

echo [CHECK 3] Installed Packages
echo [檢查 3] 已安裝的套件
if exist .venv (
    call .venv\Scripts\activate.bat
    pip list
) else (
    echo [ERROR] Virtual environment not found
    echo [錯誤] 找不到虛擬環境
    echo Please run "安裝.bat" first
    echo 請先執行「安裝.bat」
)
echo.

echo [CHECK 4] .env File Check
echo [檢查 4] .env 檔案檢查
if exist .env (
    echo [OK] .env file exists
    echo [OK] .env 檔案存在
    echo.
    echo File content (API Key hidden):
    echo 檔案內容 (API Key 已隱藏):
    type .env | findstr /V "YOUTUBE_API_KEY"
    echo YOUTUBE_API_KEY=***HIDDEN***
) else (
    echo [ERROR] .env file not found
    echo [錯誤] 找不到 .env 檔案
)
echo.

echo [CHECK 5] Test Import Packages
echo [檢查 5] 測試匯入套件
if exist .venv (
    call .venv\Scripts\activate.bat
    python -c "import flask; print('Flask:', flask.__version__)"
    python -c "import googleapiclient; print('Google API Client: OK')"
    python -c "import dotenv; print('Python-dotenv: OK')"
    python -c "import isodate; print('Isodate: OK')"
) else (
    echo [SKIP] Virtual environment not found
    echo [跳過] 找不到虛擬環境
)
echo.

echo ========================================
echo [CHECK 6] Test .env Loading
echo [檢查 6] 測試 .env 載入
echo ========================================
if exist .venv (
    call .venv\Scripts\activate.bat
    python -c "from dotenv import load_dotenv; import os; load_dotenv(); key = os.getenv('YOUTUBE_API_KEY'); print('API Key loaded:', 'YES' if key and key != 'YOUR_API_KEY_HERE' else 'NO'); print('API Key starts with AIzaSy:', 'YES' if key and key.startswith('AIzaSy') else 'NO'); print('API Key length:', len(key) if key else 0)"
)
echo.

echo ========================================
echo Diagnostic Complete
echo 診斷完成
echo ========================================
echo.
echo Please send the output above if you need help
echo 如需協助請提供以上輸出結果
echo.
pause
