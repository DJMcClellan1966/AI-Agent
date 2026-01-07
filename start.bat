@echo off
echo ====================================
echo Agentic AI Life Assistant Setup
echo ====================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your API keys:
    echo - OPENAI_API_KEY=your-key-here
    echo - ANTHROPIC_API_KEY=your-key-here (optional)
    echo - STRIPE_SECRET_KEY=your-key-here (optional)
    echo.
    echo Press any key after updating .env file...
    pause > nul
)

REM Check if frontend .env.local exists
if not exist frontend\.env.local (
    echo Creating frontend/.env.local from template...
    copy frontend\.env.example frontend\.env.local
)

echo.
echo ====================================
echo Starting with Docker Compose
echo ====================================
echo.
echo This will start:
echo - PostgreSQL database
echo - Redis cache
echo - Backend API (port 8000)
echo - Celery worker
echo - Frontend (port 3000)
echo.
echo Press Ctrl+C to stop all services
echo.

docker-compose up

echo.
echo ====================================
echo Shutdown complete
echo ====================================
