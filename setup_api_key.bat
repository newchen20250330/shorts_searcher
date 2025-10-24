@echo off
REM Force change to script directory
cd /d "%~dp0"

title Setup API Key

echo ========================================
echo Setup API Key Helper
echo ========================================
echo:

REM Check .env.example
if not exist .env.example (
    echo [ERROR] .env.example file not found
    pause
    exit /b 1
)

REM Copy to .env (always overwrite)
echo [STEP 1] Creating .env file...
copy /Y .env.example .env >nul
if errorlevel 1 (
    echo [ERROR] Failed to create .env file
    pause
    exit /b 1
)
echo [OK] File created
echo:

echo [STEP 2] Opening .env for editing...
echo:
echo IMPORTANT: Replace YOUR_API_KEY_HERE with your actual API Key
echo:
echo Press any key to open the file...
pause >nul

notepad .env

echo:
echo ========================================
echo Next steps:
echo ========================================
echo:
echo 1. Save the .env file in notepad
echo 2. Make sure you replaced YOUR_API_KEY_HERE
echo 3. Run start.bat to launch application
echo:
pause
