# Quick Start Guide

Get your AgenticAI Life Assistant up and running in minutes!

## Prerequisites

- **Node.js 18+** - For the frontend
- **Python 3.11+** - For the backend
- **Docker & Docker Compose** (optional but recommended)

## Option 1: Quick Start with Docker (Recommended)

```bash
# 1. Clone and navigate to the project
cd AI-Agent

# 2. Copy environment files
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# 3. Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here

# 4. Start everything with Docker
docker-compose up

# 5. Open your browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
```

## Option 2: Manual Setup

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment file
cd ..
cp .env.example .env
# Edit .env and add your API keys

# 6. Start the backend
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup (in a new terminal)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Copy environment file
cp .env.example .env.local

# 4. Start the frontend
npm run dev
```

### Worker Setup (in a third terminal, optional)

```bash
# For async task processing
cd backend
celery -A app.worker worker --loglevel=info -P solo
```

## Using the App

### 1. Create an Account
- Go to http://localhost:3000
- Click "Sign up for free"
- Enter your details

### 2. Create Your First Agent
- Click "Agents" in the sidebar
- Click "Create Agent"
- Choose an agent type (Email, Scheduler, Finance, etc.)
- Configure permissions
- Click "Create Agent"

### 3. Monitor Tasks
- Agents will create tasks as they work
- Review pending tasks in the "Tasks" section
- Approve or reject tasks as needed

### 4. Connect Integrations
- Go to "Integrations"
- Connect your email, calendar, etc.
- Agents will use these to automate your life!

## Environment Variables

### Required
```env
# OpenAI API Key (for LLM capabilities)
OPENAI_API_KEY=sk-your-key-here

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost:5432/agentic_ai

# Redis (for task queue)
REDIS_URL=redis://localhost:6379

# JWT Secret (generate a secure random string)
SECRET_KEY=your-super-secret-key-here
```

### Optional
```env
# Anthropic API (alternative LLM)
ANTHROPIC_API_KEY=sk-ant-your-key

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_test_your-key
STRIPE_WEBHOOK_SECRET=whsec_your-secret

# Google OAuth (for Gmail/Calendar)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

## Default Credentials

When running locally, you can create any account. The free tier includes:
- 2 AI agents
- 50 tasks per month
- Basic features

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Make sure virtual environment is activated
- Check that all dependencies installed: `pip install -r requirements.txt`

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### Database errors
- Make sure PostgreSQL is running
- Check DATABASE_URL in .env

### Task queue not working
- Make sure Redis is running
- Check REDIS_URL in .env
- Start the Celery worker

## Next Steps

- Read the [full documentation](./PROJECT_OVERVIEW.md)
- Explore the [API docs](http://localhost:8000/api/docs)
- Check out the [architecture guide](./ARCHITECTURE.md)

---

**Need help?** Open an issue on GitHub or check the documentation.
