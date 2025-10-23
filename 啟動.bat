@echo off
chcp 65001 >nul
title YouTube 短影片搜尋器

echo ========================================
echo    YouTube 短影片搜尋器
echo ========================================
echo.

REM 檢查虛擬環境是否存在
if not exist .venv (
    echo ❌ 錯誤：尚未安裝
    echo.
    echo 請先執行「安裝.bat」
    echo.
    pause
    exit /b 1
)

REM 檢查 .env 檔案
if not exist .env (
    echo ❌ 錯誤：找不到 .env 檔案
    echo.
    echo 請複製 .env.example 為 .env 並填入你的 API Key
    echo.
    pause
    exit /b 1
)

REM 啟動虛擬環境
call .venv\Scripts\activate.bat

REM 啟動程式
echo 🚀 啟動 YouTube 短影片搜尋器...
echo.
echo 📌 程式啟動後，請開啟瀏覽器並前往：
echo    http://127.0.0.1:5000
echo.
echo 💡 按 Ctrl+C 可停止程式
echo ========================================
echo.

python app.py

pause
