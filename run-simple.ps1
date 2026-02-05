# Simplified run: backend + frontend in one command (no Docker, no Redis/Celery).
# Prerequisites: .env with DATABASE_URL=sqlite:///./agentic_ai.db and USE_CELERY=false (see .env.example).
# From project root: .\run-simple.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
if (-not $root) { $root = Get-Location }

# Ensure backend has .env (uvicorn runs from backend/ and loads backend/.env)
if ((Test-Path (Join-Path $root ".env")) -and -not (Test-Path (Join-Path $root "backend\.env"))) {
    Copy-Item (Join-Path $root ".env") (Join-Path $root "backend\.env")
}

# Start backend in a new window
$backendScript = @"
Set-Location '$root'
if (Test-Path '.venv\Scripts\Activate.ps1') { . '.venv\Scripts\Activate.ps1' }
Set-Location backend
python -m uvicorn app.main:app --reload --port 8001
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Give backend a moment to bind
Start-Sleep -Seconds 3

# Start frontend in this window
Set-Location (Join-Path $root "frontend")
if (-not (Test-Path "node_modules")) { npm install }
npm run dev
