@echo off
echo ============================================
echo   OpenRouter API Setup
echo ============================================
echo.
echo This will configure your AI model for
echo extracting DAGs from images.
echo.
echo API Key: Already configured!
echo.
echo Press any key to choose your model...
pause > nul

cd backend
python setup_api_key.py

echo.
echo ============================================
pause

