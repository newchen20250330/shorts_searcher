@echo off
chcp 65001 >nul
echo ========================================
echo    Setup API Key Helper
echo    設定 API Key 輔助工具
echo ========================================
echo.

REM Check if .env.example exists
if not exist .env.example (
    echo [ERROR] .env.example file not found
    echo [錯誤] 找不到 .env.example 檔案
    pause
    exit /b 1
)

REM Copy .env.example to .env if not exists
if exist .env (
    echo [INFO] .env file already exists
    echo [資訊] .env 檔案已存在
    echo.
    echo Do you want to overwrite it? (Y/N)
    echo 要覆蓋它嗎？(Y/N)
    set /p overwrite=
    if /i not "%overwrite%"=="Y" (
        echo [CANCELLED] Operation cancelled
        echo [取消] 操作已取消
        pause
        exit /b 0
    )
)

echo.
echo [STEP 1] Copying .env.example to .env
echo [步驟 1] 複製 .env.example 為 .env
copy .env.example .env >nul
echo [OK] File created
echo [OK] 檔案已建立
echo.

echo [STEP 2] Opening .env file for editing
echo [步驟 2] 開啟 .env 檔案進行編輯
echo.
echo Please replace YOUR_API_KEY_HERE with your actual YouTube API Key
echo 請將 YOUR_API_KEY_HERE 替換成你的 YouTube API Key
echo.
echo Press any key to open the file...
echo 按任意鍵開啟檔案...
pause >nul

notepad .env

echo.
echo ========================================
echo [INFO] Next steps:
echo [資訊] 下一步:
echo ========================================
echo.
echo 1. Make sure you saved the .env file
echo    確認你已儲存 .env 檔案
echo.
echo 2. Make sure you replaced YOUR_API_KEY_HERE with your API Key
echo    確認你已將 YOUR_API_KEY_HERE 替換成你的 API Key
echo.
echo 3. Run "啟動.bat" to start the application
echo    執行「啟動.bat」啟動程式
echo.
echo For API Key instructions, see "使用說明.txt"
echo API Key 取得方式請參考「使用說明.txt」
echo.
pause
