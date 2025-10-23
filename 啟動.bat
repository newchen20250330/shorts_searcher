@echo off
chcp 65001 >nul
title YouTube Shorts Searcher

echo ========================================
echo    YouTube Shorts Searcher
echo    YouTube 短影片搜尋器
echo ========================================
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo [ERROR] Not installed yet
    echo [錯誤] 尚未安裝
    echo.
    echo Please run "安裝.bat" first
    echo 請先執行「安裝.bat」
    echo.
    pause
    exit /b 1
)

REM Check .env file
if not exist .env (
    echo [ERROR] .env file not found
    echo [錯誤] 找不到 .env 檔案
    echo.
    echo Please run "設定API_Key.bat" to create .env file
    echo 請執行「設定API_Key.bat」建立 .env 檔案
    echo.
    echo Or manually:
    echo 或手動:
    echo   1. Copy .env.example to .env
    echo      複製 .env.example 為 .env
    echo   2. Edit .env and add your API Key
    echo      編輯 .env 並填入你的 API Key
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start application
echo [STARTING] YouTube Shorts Searcher...
echo [啟動中] YouTube 短影片搜尋器...
echo.
echo The browser will open automatically in 3 seconds...
echo 瀏覽器將在 3 秒後自動開啟...
echo.
echo If not, please open your browser and go to:
echo 如果沒有自動開啟，請手動開啟瀏覽器並前往:
echo.
echo    http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the application
echo 按 Ctrl+C 可停止程式
echo ========================================
echo.

REM Wait 3 seconds then open browser
start /B timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000

REM Run Python app and keep window open on error
python app.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Application failed to start
    echo [錯誤] 程式啟動失敗
    echo ========================================
    echo.
    echo Please check the error message above
    echo 請查看上方的錯誤訊息
    echo.
    echo Common issues:
    echo 常見問題:
    echo   1. API Key not set or invalid
    echo      API Key 未設定或無效
    echo   2. Missing packages - try reinstalling
    echo      缺少套件 - 嘗試重新安裝
    echo   3. Port 5000 already in use
    echo      Port 5000 已被佔用
    echo.
    echo For detailed diagnosis, run "診斷.bat"
    echo 詳細診斷請執行「診斷.bat」
    echo.
)

pause
