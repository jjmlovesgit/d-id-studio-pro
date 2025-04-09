@echo off
cd /d %~dp0

echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

echo 🚀 Launching D-ID Studio Pro...
python app.py

echo.
pause
