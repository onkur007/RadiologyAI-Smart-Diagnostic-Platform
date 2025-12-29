@echo off
REM Quick setup script for Windows
REM Run this to set up the project quickly

echo ========================================
echo AI-Powered Radiology Assistant
echo Quick Setup Script for Windows
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if PostgreSQL is accessible
psql --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PostgreSQL command line tools not found
    echo Make sure PostgreSQL is installed and in PATH
    echo.
)

echo Step 1: Creating virtual environment...
if exist venv (
    echo [INFO] Virtual environment already exists
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

echo Step 3: Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo Step 4: Checking configuration...
if exist .env (
    echo [OK] .env file exists
) else (
    echo [INFO] Creating .env file from template...
    copy .env.example .env
    echo [WARNING] Please edit .env file with your credentials:
    echo   - DATABASE_URL
    echo   - SECRET_KEY
    echo   - GEMINI_API_KEY
    echo.
    echo Open .env file now? (Y/N)
    set /p OPEN_ENV=
    if /i "%OPEN_ENV%"=="Y" notepad .env
)
echo.

echo Step 5: Database setup...
echo Would you like to initialize the database now? (Y/N)
set /p INIT_DB=
if /i "%INIT_DB%"=="Y" (
    python init_db.py
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Make sure PostgreSQL is running
echo 2. Update .env file with your credentials
echo 3. Run: uvicorn app.main:app --reload
echo 4. Open: http://localhost:8000/docs
echo.
echo Quick commands:
echo   - Start app: uvicorn app.main:app --reload
echo   - Run tests: pytest tests/
echo   - Init DB: python init_db.py
echo.
echo Documentation:
echo   - Quick Start: QUICKSTART.md
echo   - Installation: INSTALLATION.md
echo   - Beginners: BEGINNERS_GUIDE.md
echo.

pause
