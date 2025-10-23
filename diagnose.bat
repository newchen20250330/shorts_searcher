@echo off
title Diagnostic Tool

echo ========================================
echo System Diagnostic Tool
echo ========================================
echo.

echo [CHECK 1] Python Version
python --version
echo.

echo [CHECK 2] Python Path
python -c "import sys; print(sys.executable)"
echo.

echo [CHECK 3] Virtual Environment
if exist .venv (
    echo [OK] .venv folder exists
) else (
    echo [ERROR] .venv folder not found
    echo Please run install.bat first
)
echo.

echo [CHECK 4] .env File
if exist .env (
    echo [OK] .env file exists
) else (
    echo [ERROR] .env file not found
    echo Please run setup_api_key.bat
)
echo.

echo [CHECK 5] Installed Packages
if exist .venv (
    call .venv\Scripts\activate.bat
    pip list
) else (
    echo [SKIP] No virtual environment
)
echo.

echo [CHECK 6] Test Imports
if exist .venv (
    call .venv\Scripts\activate.bat
    python -c "import flask; print('Flask: OK')"
    python -c "import googleapiclient; print('Google API: OK')"
    python -c "import dotenv; print('Python-dotenv: OK')"
    python -c "import isodate; print('Isodate: OK')"
) else (
    echo [SKIP] No virtual environment
)
echo.

echo ========================================
echo Diagnostic Complete
echo ========================================
pause
