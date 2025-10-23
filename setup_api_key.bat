@echo off
title Setup API Key

echo ========================================
echo Setup API Key Helper
echo ========================================
echo.

REM Check .env.example
if not exist .env.example (
    echo [ERROR] .env.example file not found
    pause
    exit /b 1
)

REM Copy to .env
if exist .env (
    echo [INFO] .env file already exists
    echo.
    echo Overwrite? (Y/N)
    set /p overwrite=
    if /i not "%overwrite%"=="Y" (
        echo [CANCELLED] Operation cancelled
        pause
        exit /b 0
    )
)

echo.
echo [STEP 1] Creating .env file...
copy .env.example .env >nul
echo [OK] File created
echo.

echo [STEP 2] Opening .env for editing...
echo.
echo Replace YOUR_API_KEY_HERE with your actual API Key
echo.
echo Press any key to open the file...
pause >nul

notepad .env

echo.
echo ========================================
echo Next steps:
echo ========================================
echo.
echo 1. Make sure you saved the .env file
echo 2. Make sure you replaced YOUR_API_KEY_HERE
echo 3. Run "start.bat" to launch application
echo.
echo For API Key guide, see README.md
echo.
pause
