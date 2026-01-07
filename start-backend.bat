@echo off
echo ====================================
echo Manual Setup - Backend
echo ====================================
echo.

cd backend

REM Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ====================================
echo Starting Backend Server
echo ====================================
echo.
echo Backend will be available at: http://localhost:8000
echo API documentation: http://localhost:8000/api/docs
echo.

uvicorn app.main:app --reload --port 8000
