# Local Agent IDE – Setup Guide

## 📋 Prerequisites

Before getting started, ensure you have the following installed:

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose** (recommended)
- **PostgreSQL 15+** (if not using Docker)
- **Redis** (if not using Docker)

## ⚡ Simplified run (no Docker, no PostgreSQL, no Redis)

You can run the app with **one database file** and **no Redis/Celery**:

1. **Copy env and use simplified defaults**
   - `copy .env.example .env` (and `frontend\.env.example` → `frontend\.env.local`).
   - `.env` already sets `DATABASE_URL=sqlite:///./agentic_ai.db` and `USE_CELERY=false`. No PostgreSQL or Redis needed.

2. **Install and start (two options)**
   - **One command (PowerShell):** from project root run `.\run-simple.ps1`. This opens the backend in a new window and runs the frontend in the current window.
   - **Two terminals:** in one run `cd backend` then `uvicorn app.main:app --reload --port 8000` (with `.venv` activated from root). In the other run `cd frontend` then `npm run dev`.

3. **Open** http://localhost:3000 (frontend) and http://localhost:8000 (API). The SQLite DB file is created in `backend/` on first run. Task execution runs in-process (no Celery worker).

To use **PostgreSQL + Redis + Celery** again, set `DATABASE_URL` and `USE_CELERY=true` in `.env` and start Postgres, Redis, and the Celery worker as in Manual Setup below.

## 🚀 Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   cd AI-Agent
   ```

2. **Copy environment files**
   ```bash
   copy .env.example .env
   cd frontend
   copy .env.example .env.local
   cd ..
   ```

3. **Edit `.env`** (optional for local-only)
   - For **local use without API keys**: leave `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` empty; keep `USE_LOCAL_LLM=true` and use Ollama (see “Run locally without API keys” above).
   - To use cloud AI: set `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY`. Update other settings as needed.

4. **Start all services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

## 💻 Manual Setup (Without Docker)

### Backend Setup

**Recommended: use a dedicated virtual environment.** Install only this project’s dependencies in it. That avoids conflicts with other tools (e.g. `build`, `poetry`, `streamlit`) that may be installed in your system or base Python.

1. **From the project root, create and activate a venv**
   ```bash
   cd AI-Agent-1
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   On Windows CMD: `.venv\Scripts\activate.bat`

2. **Install backend dependencies**
   ```bash
   pip install -r backend\requirements.txt
   ```

3. **Navigate to backend for the next steps**
   ```bash
   cd backend
   ```
   (If you created the venv inside `backend` instead, run `pip install -r requirements.txt` there.)

4. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

5. **Start PostgreSQL and Redis**
   - Option 1: Use Docker for just the databases
     ```bash
     docker-compose up -d postgres redis
     ```
   - Option 2: Install and start them manually

6. **Run database migrations**
   ```bash
   # The tables will be created automatically when you start the app
   ```

7. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

8. **Start the Celery worker** (in a new terminal, activate the same venv first)
   ```bash
   cd AI-Agent-1
   .\.venv\Scripts\Activate.ps1
   cd backend
   celery -A app.agents.executor worker --loglevel=info -P solo
   ```

### Frontend Setup

1. **Navigate to frontend directory** (new terminal)
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   copy .env.example .env.local
   # Edit .env.local if needed
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Open http://localhost:3000 in your browser

## 🔧 Configuration

### Required API Keys

1. **OpenAI API Key** (Required for AI agents)
   - Get from: https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_API_KEY=sk-...`

2. **Anthropic API Key** (Optional, for Claude models)
   - Get from: https://console.anthropic.com/
   - Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

3. **Stripe API Key** (Optional, for payments)
   - Get from: https://dashboard.stripe.com/apikeys
   - Add to `.env`: `STRIPE_SECRET_KEY=sk_test_...`

### Database Configuration

The default configuration uses:
- PostgreSQL on `localhost:5432`
- Database name: `agentic_ai`
- Username: `postgres`
- Password: `postgres`

Update `DATABASE_URL` in `.env` to change these settings.

## 🎯 First Steps

1. **Register** at http://localhost:3000 (Sign Up).
2. **Open the IDE** – click **IDE** in the sidebar. Set **Workspace root** to a folder on your machine.
3. **Chat with the agent** – in the IDE or on the **Agent** page. The agent can read files, suggest edits, and run commands (you approve first).
4. **Build** – use the **Build** page to describe an app in chat and get a single HTML file.

### Build: Synthesis-style single file (open in browser)

Generated apps use a **Synthesis-style** flow: conversation → spec → one **index file** you can open in the browser with no server.

- **Default**: `BUILD_SINGLE_FILE=true` in `.env` — the build produces a single `index.html` with inline CSS and JS. Download the project zip (one file) or open it in the browser.
- **Open in browser (no download)**: `GET /api/v1/build/projects/{project_id}/open` returns the HTML; open that URL in a new tab to run the app.
- **Multi-file**: Set `BUILD_SINGLE_FILE=false` to get separate `index.html`, `styles.css`, and `app.js` (e.g. for editing in an IDE); then use **Download** and open `index.html` from the zip (it still references the other two files).

## 🛠️ Development

### Backend Development

```bash
cd backend

# Run tests
pytest

# Format code
black app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Run type checking
npm run type-check

# Lint code
npm run lint

# Build for production
npm run build
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use** or **WinError 10013** (access to socket forbidden)
   - Another process may be using the port, or Windows may be blocking it. Use a different port:
     ```bash
     uvicorn app.main:app --reload --port 8001
     ```
   - If you use port 8001 (or another port), set the frontend API URL to match, e.g. in `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8001`
   - To see what is using port 8000 (PowerShell): `Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess; Get-Process -Id <PID>`
   - Or change ports in `docker-compose.yml` when using Docker.

2. **Database connection error**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in `.env`

3. **API key errors**
   - Verify API keys are correct in `.env`
   - Restart backend after updating `.env`

4. **Celery not starting on Windows**
   - Use `-P solo` flag: `celery -A app.agents.executor worker -P solo`

5. **Frontend can't connect to backend**
   - Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
   - Ensure backend is running on correct port

6. **pip dependency conflicts** (e.g. `packaging`, `importlib-metadata`, conflicts with `build`/`poetry`/`streamlit`)
   - Use a **dedicated virtual environment** and install only `backend/requirements.txt` in it (see Backend Setup above).
   - Keep tools like `build`, `poetry`, or `streamlit` in a separate env or system install so their versions don’t clash with the backend.

## 📚 Next Steps

- Read the [Agent Development Guide](./docs/agents.md)
- Explore the [API Documentation](http://localhost:8000/api/docs)
- Check out the [Integration Guide](./docs/integrations.md)

## 🆘 Getting Help

- Check the documentation in the `docs/` folder
- Open an issue on GitHub
- Contact support at support@agentic-ai.app

## 🎉 You're All Set!

Your Agentic AI Life Assistant is now running. Start exploring and let the AI agents help you manage your daily tasks!
