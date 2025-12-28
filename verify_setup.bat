@echo off
echo ========================================
echo  DAG Optimizer - Setup Verification
echo ========================================
echo.

set ERROR_COUNT=0

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    set /a ERROR_COUNT+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python %%i found
)
echo.

echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js 18+
    set /a ERROR_COUNT+=1
) else (
    for /f %%i in ('node --version') do echo ✅ Node.js %%i found
)
echo.

echo [3/5] Checking npm installation...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm not found! Please install Node.js with npm
    set /a ERROR_COUNT+=1
) else (
    for /f %%i in ('npm --version') do echo ✅ npm %%i found
)
echo.

echo [4/5] Checking Graphviz installation...
dot -V >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Graphviz not found or not in PATH
    echo    Download from: https://graphviz.org/download/
    echo    Note: This is optional but recommended for better visualizations
) else (
    for /f "tokens=*" %%i in ('dot -V 2^>^&1') do echo ✅ %%i
)
echo.

echo [5/5] Checking project structure...
if not exist "backend\main.py" (
    echo ❌ Backend files missing!
    set /a ERROR_COUNT+=1
) else (
    echo ✅ Backend files found
)

if not exist "frontend\package.json" (
    echo ❌ Frontend files missing!
    set /a ERROR_COUNT+=1
) else (
    echo ✅ Frontend files found
)
echo.

echo ========================================
if %ERROR_COUNT% equ 0 (
    echo  ✅ Setup verification passed!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Run 'install_dependencies.bat' to install packages
    echo 2. Run 'start_all.bat' to start the application
) else (
    echo  ❌ Setup verification failed with %ERROR_COUNT% error(s)
    echo ========================================
    echo.
    echo Please fix the errors above and try again.
)
echo.
pause

