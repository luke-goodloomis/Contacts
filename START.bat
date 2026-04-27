@echo off
REM Contact Manager Application Launcher
REM This script starts the FastAPI server and opens the web interface

echo ============================================================
echo   Contact Manager with OCR
echo   Starting application...
echo ============================================================

cd /d J:\contacts\app

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if Tesseract is installed
where tesseract >nul 2>&1
if errorlevel 1 (
    echo WARNING: Tesseract OCR not found in PATH
    echo OCR features will not work until Tesseract is installed
    echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    pause
)

REM Check if dependencies are installed
python -c "import fastapi, uvicorn, pydantic, PIL, pytesseract" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing required dependencies...
    echo This may take a minute...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo   Starting FastAPI server...
echo   Opening web interface in browser...
echo ============================================================
echo.
echo   URL: http://localhost:8000
echo.
echo   Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Add to Windows Firewall exceptions (optional, allows network access)
echo.
echo Adding to Windows Firewall (allows access from other devices on network)...
netsh advfirewall firewall add rule name="Contact Manager" dir=in action=allow program="python.exe" enable=yes >nul 2>&1

REM Start server in background and open browser
echo.
echo Starting server...
start http://localhost:8000
python main.py

pause
