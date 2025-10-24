@echo off
REM Force change to script directory
cd /d "%~dp0"

title YouTube Shorts Searcher - Install

echo ========================================
echo YouTube Shorts Searcher - Installation
echo ========================================
echo:

REM Check if running in correct directory
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found
    echo:
    echo You must run this script in the correct folder
    echo Make sure you are in the folder containing:
    echo   - install.bat
    echo   - requirements.txt
    echo   - app.py
    echo   - templates folder
    echo:
    echo Current directory:
    cd
    echo:
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo:
    echo Please install Python 3.8 or newer from:
    echo https://www.python.org/downloads/
    echo:
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo:
    pause
    exit /b 1
)

echo [OK] Python detected
python --version
echo:

REM Create virtual environment
echo [STEP 1] Creating virtual environment...
if exist .venv (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo:

REM Install packages
echo [STEP 2] Installing packages...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Package installation failed
    echo:
    echo This might be due to:
    echo   1. Network connection issues
    echo   2. Python version incompatibility
    echo   3. Missing build tools
    echo:
    echo Try running diagnose.bat for more info
    echo:
    pause
    exit /b 1
)

echo:
echo ========================================
echo [SUCCESS] Installation completed!
echo ========================================
echo:
echo Next steps:
echo:
echo OPTION 1 (Recommended): Run "setup_api_key.bat"
echo   - Automatically creates .env file
echo   - Opens editor for you to add API Key
echo:
echo OPTION 2 (Manual):
echo   1. Copy .env.example to .env
echo   2. Edit .env and add your YouTube API Key
echo:
echo After setup, run "start.bat" to launch
echo:
echo For API Key guide, see README.md
echo:
pause
