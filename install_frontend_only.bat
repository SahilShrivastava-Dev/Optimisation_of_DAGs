@echo off
echo ========================================
echo  Installing Frontend Dependencies Only
echo ========================================
echo.

cd frontend

echo Cleaning npm cache...
call npm cache clean --force

echo.
echo Installing dependencies...
call npm install

echo.
if %errorlevel% equ 0 (
    echo ✅ Frontend dependencies installed successfully!
    echo.
    echo You can now run: npm run dev
) else (
    echo ❌ Installation failed!
)

echo.
pause

