@echo off
REM NYC Taxi Analytics - One-Click Render Deployment Script (Windows)
REM This script prepares your application for Render deployment

echo 🚀 NYC Taxi Analytics - Render Deployment Setup
echo ================================================

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "backend\app.py" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

echo ✅ Project structure verified

REM Check if render.yaml exists
if not exist "render.yaml" (
    echo ❌ Error: render.yaml not found. Please ensure all deployment files are present.
    pause
    exit /b 1
)

echo ✅ Deployment configuration found

REM Verify PostgreSQL schema exists
if not exist "db\schema_postgresql.sql" (
    echo ❌ Error: PostgreSQL schema not found. Please ensure db\schema_postgresql.sql exists.
    pause
    exit /b 1
)

echo ✅ PostgreSQL schema verified

REM Check if frontend is configured for Render
findstr /C:"onrender.com" frontend\main.js >nul
if errorlevel 1 (
    echo ❌ Error: Frontend not configured for Render. Please update frontend\main.js
    pause
    exit /b 1
)

echo ✅ Frontend Render configuration verified

echo.
echo 🎉 Your application is ready for Render deployment!
echo.
echo Next steps:
echo 1. Push all changes to GitHub:
echo    git add .
echo    git commit -m "Add Render deployment configuration"
echo    git push
echo.
echo 2. Go to https://render.com and create a new Blueprint
echo 3. Connect your GitHub repository
echo 4. Render will automatically:
echo    - Create PostgreSQL database with schema
echo    - Deploy backend API service
echo    - Deploy frontend static site
echo    - Configure all environment variables
echo.
echo 5. Your app will be available at:
echo    - Backend: https://nyc-taxi-backend.onrender.com
echo    - Frontend: https://nyc-taxi-frontend.onrender.com
echo.
echo ✨ Happy deploying!
pause
