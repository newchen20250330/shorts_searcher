@echo off
chcp 65001 >nul
echo ========================================
echo Simple Diagnostic
echo 簡易診斷
echo ========================================
echo.

echo Python version:
python --version
echo.

echo Virtual environment:
if exist .venv (echo EXISTS) else (echo NOT FOUND)
echo.

echo .env file:
if exist .env (echo EXISTS) else (echo NOT FOUND)
echo.

echo Press any key to test Python...
pause >nul

if exist .venv (
    call .venv\Scripts\activate.bat
    python --version
    echo.
    echo Testing app.py...
    python -c "print('Python is working')"
)

echo.
pause
