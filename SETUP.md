# Agentic AI Life Assistant - Setup Guide

## 📋 Prerequisites

Before getting started, ensure you have the following installed:

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose** (recommended)
- **PostgreSQL 15+** (if not using Docker)
- **Redis** (if not using Docker)

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

3. **Edit `.env` file with your API keys**
   - Add your OpenAI API key: `OPENAI_API_KEY=sk-...`
   - Add your Anthropic API key (optional): `ANTHROPIC_API_KEY=sk-ant-...`
   - Update other settings as needed

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

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

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

8. **Start the Celery worker** (in a new terminal)
   ```bash
   cd backend
   venv\Scripts\activate
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

1. **Register a new account**
   - Go to http://localhost:3000
   - Click "Sign Up"
   - Create your account

2. **Create your first agent**
   - Navigate to "Agents" page
   - Click "Create Agent"
   - Choose agent type (Email, Scheduler, Finance, etc.)
   - Configure permissions

3. **Connect integrations** (Coming soon)
   - Connect your email
   - Link calendar
   - Add other services

4. **Review and approve tasks**
   - Check the "Tasks" page for pending approvals
   - Approve or reject agent-suggested actions

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

1. **Port already in use**
   - Change ports in `docker-compose.yml` or stop conflicting services

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
