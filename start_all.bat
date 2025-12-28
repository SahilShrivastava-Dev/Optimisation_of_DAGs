@echo off
echo ========================================
echo  DAG Optimizer - Starting Application
echo ========================================
echo.

echo Starting Backend Server...
start "DAG Optimizer - Backend" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "DAG Optimizer - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo  Servers Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to close this window...
pause > nul

