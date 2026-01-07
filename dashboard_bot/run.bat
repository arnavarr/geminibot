@echo off
REM Dashboard Bot Execution Script for Windows

cd /d "%~dp0"

IF EXIST ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) ELSE (
    echo [ERROR] Virtual environment not found!
    echo Please run 'pip install -r requirements.txt' or create venv first.
    pause
    exit /b 1
)

echo Starting Dashboard Bot...
python agent.py %*

if %errorlevel% neq 0 (
    echo [ERROR] Bot execution failed.
    pause
)
