@echo off
echo 🚀 TON AI Trading Bot - Installation Script
echo.

REM Check Python
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ⚠️  Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Dependencies installed
echo.

REM Create .env file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo ✅ .env file created
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and add your credentials!
    echo    - WALLET_MNEMONIC (24 words^)
    echo    - ANTHROPIC_API_KEY
) else (
    echo ⚠️  .env file already exists
)
echo.

echo ✅ Installation complete!
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo 2. Run: python test_setup.py
echo 3. Run: python main.py
echo.
pause
