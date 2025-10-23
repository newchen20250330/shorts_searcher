@echo off
title YouTube Shorts Searcher

echo ========================================
echo YouTube Shorts Searcher
echo ========================================
echo.

REM Check virtual environment
if not exist .venv (
    echo [ERROR] Not installed yet
    echo.
    echo Please run "install.bat" first
    echo.
    pause
    exit /b 1
)

REM Check .env file
if not exist .env (
    echo [ERROR] .env file not found
    echo.
    echo Please run "setup_api_key.bat" to create .env file
    echo.
    echo Or manually:
    echo   1. Copy .env.example to .env
    echo   2. Edit .env and add your API Key
    echo.
    pause
    exit /b 1
)

REM Activate and start
call .venv\Scripts\activate.bat

echo [STARTING] Application starting...
echo.
echo Browser will open in 3 seconds at:
echo    http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

REM Open browser after delay
start /B timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000

REM Run app
python app.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Application failed to start
    echo ========================================
    echo.
    echo Check error message above
    echo.
    echo Common issues:
    echo   1. API Key not set or invalid
    echo   2. Missing packages - try reinstalling
    echo   3. Port 5000 already in use
    echo.
    echo Run "diagnose.bat" for detailed check
    echo.
)

pause
