@echo off
echo ====================================
echo Starting Celery Worker
echo ====================================
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting Celery worker...
echo.

celery -A app.agents.executor worker --loglevel=info -P solo
