@echo off
REM One-time setup for Windows. Double-click or run: setup_windows.bat
cd /d "%~dp0backend"
python -m venv venv || goto :err
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt || goto :err
if not exist .env copy .env.example .env
cd ..\frontend
call npm install || goto :err
echo Setup done. Edit backend\.env, then see README.md section 4 to run.
goto :eof
:err
echo Setup failed. Check the error above.
exit /b 1
