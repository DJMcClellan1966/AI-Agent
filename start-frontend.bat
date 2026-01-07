@echo off
echo ====================================
echo Manual Setup - Frontend
echo ====================================
echo.

cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo.
echo ====================================
echo Starting Frontend Development Server
echo ====================================
echo.
echo Frontend will be available at: http://localhost:3000
echo.

call npm run dev
