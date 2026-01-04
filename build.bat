@echo off
REM Build script for Windows
REM Automatically creates a venv and builds the app

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo === DPS-150 Native App Builder ===
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Error: Python is not installed
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYVERSION=%%i
echo + Python found: !PYVERSION!
echo.

REM Create virtual environment if not present
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo + Virtual environment created
) else (
    echo + Virtual environment already exists
)

echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements-build.txt --quiet
echo + Dependencies installed

echo.
echo Starting build process...
echo.
python build.py

echo.
echo === Build completed! ===
echo Die Anwendung befindet sich im 'dist' Ordner
echo    - dist\DPS150-Control.exe
echo.

call deactivate
endlocal
