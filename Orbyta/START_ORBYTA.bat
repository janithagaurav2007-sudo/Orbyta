@echo off
title ORBYTA - Women's Health Companion
echo.
echo ==========================================
echo          ORBYTA - STARTING APP
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10+ and try again.
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo Node.js/npm was not found. Install Node.js 18+ and try again.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  cd backend
  python -m venv .venv
  cd ..
)

echo Installing backend packages...
call backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

if not exist "frontend\node_modules" (
  echo Installing frontend packages...
  cd frontend
  call npm install
  cd ..
)

echo.
echo Starting backend and frontend...
start "ORBYTA Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
start "ORBYTA Frontend" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:5173"

echo.
echo ORBYTA is starting.
echo Frontend: http://127.0.0.1:5173
echo Backend:  http://127.0.0.1:8000/docs
echo.
pause
