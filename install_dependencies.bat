@echo off
echo ========================================
echo  DAG Optimizer - Installing Dependencies
echo ========================================
echo.

echo [1/2] Installing Backend Dependencies...
echo ----------------------------------------
pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo Backend dependencies installed successfully!
echo.

echo [2/2] Installing Frontend Dependencies...
echo ----------------------------------------
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..
echo Frontend dependencies installed successfully!
echo.

echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure Graphviz is installed on your system
echo 2. Run 'start_all.bat' to start the application
echo.
pause

