# 🚀 Quick Start Guide

Get your Agentic AI Life Assistant up and running in minutes!

## ⚡ Option 1: Docker (Fastest - Recommended)

### Prerequisites
- Docker Desktop installed
- OpenAI API key

### Steps

1. **Clone/Navigate to project**
   ```bash
   cd AI-Agent
   ```

2. **Set up environment**
   ```bash
   # Copy environment file
   copy .env.example .env
   
   # Edit .env and add your OpenAI API key
   notepad .env
   # Add: OPENAI_API_KEY=sk-your-key-here
   ```

3. **Start everything**
   ```bash
   docker-compose up
   ```
   
   That's it! Wait for services to start (2-3 minutes first time)

4. **Access the app**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/api/docs

5. **Create an account**
   - Go to http://localhost:3000
   - Sign up with email and password
   - Start creating agents!

---

## 💻 Option 2: Manual Setup (More Control)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ running locally
- Redis running locally

### Backend Setup

1. **Terminal 1 - Backend API**
   ```bash
   # Run the setup script
   start-backend.bat
   ```
   
   Or manually:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   
   # Copy and edit .env
   copy .env.example .env
   notepad .env  # Add your API keys
   
   # Start backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Terminal 2 - Celery Worker**
   ```bash
   # Run the worker script
   start-worker.bat
   ```
   
   Or manually:
   ```bash
   cd backend
   venv\Scripts\activate
   celery -A app.agents.executor worker --loglevel=info -P solo
   ```

### Frontend Setup

3. **Terminal 3 - Frontend**
   ```bash
   # Run the setup script
   start-frontend.bat
   ```
   
   Or manually:
   ```bash
   cd frontend
   npm install
   copy .env.example .env.local
   npm run dev
   ```

### Access
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

---

## 🎯 First Steps After Setup

### 1. Create Your Account
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Enter your details
4. Log in

### 2. Create Your First Agent

**Email Agent Example:**
1. Navigate to "Agents" page
2. Click "Create Agent"
3. Select "Email" as agent type
4. Name it: "Email Manager"
5. Configure:
   - ✅ Requires approval: ON (recommended)
   - ❌ Can execute autonomously: OFF (for now)
   - Max daily tasks: 10
6. Click "Create"

**Scheduler Agent Example:**
1. Create another agent
2. Select "Scheduler" type
3. Name it: "Calendar Assistant"
4. Set permissions for calendar access
5. Save

### 3. Review Agent Suggestions

Agents will start analyzing patterns and suggesting tasks. Check:
- Dashboard for overview
- Tasks page for pending approvals
- Approve or reject suggested actions

### 4. Connect Integrations (Coming Soon)

Future integrations:
- Gmail/Outlook
- Google Calendar
- Banking APIs

---

## 📝 Example Use Cases

### Use Case 1: Email Management
1. Email Agent analyzes your inbox
2. Categorizes emails (urgent, important, spam)
3. Drafts responses to common emails
4. Schedules follow-ups
5. You review and approve

### Use Case 2: Appointment Booking
1. Scheduler Agent monitors your calendar
2. Finds conflicts
3. Suggests rescheduling options
4. Books appointments when you approve
5. Sends reminders

### Use Case 3: Bill Negotiation
1. Finance Agent tracks your bills
2. Identifies high costs
3. Prepares negotiation scripts
4. You review and approve
5. Agent helps you save money

---

## 🛠️ Configuration

### Environment Variables

**Backend (.env):**
```env
# Required
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agentic_ai
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-secret-key-change-this

# Optional
ANTHROPIC_API_KEY=sk-ant-your-key-here
STRIPE_SECRET_KEY=sk_test_your-key-here
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## ✅ Verify Installation

### Check Backend
```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","version":"1.0.0","service":"agentic-ai-api"}
```

### Check Frontend
- Open http://localhost:3000
- Should see login/signup page

### Check API Docs
- Open http://localhost:8000/api/docs
- Should see Swagger UI with all endpoints

---

## 🐛 Troubleshooting

### Problem: Port already in use
**Solution:**
```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Or change ports in docker-compose.yml or .env
```

### Problem: Database connection error
**Solution:**
```bash
# Make sure PostgreSQL is running
# Check connection string in .env
# If using Docker:
docker-compose up -d postgres
```

### Problem: OpenAI API error
**Solution:**
- Verify API key in .env is correct
- Check you have credits at https://platform.openai.com/account/billing
- Restart backend after updating .env

### Problem: Frontend can't connect to backend
**Solution:**
- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Check browser console for CORS errors

### Problem: Celery worker not starting on Windows
**Solution:**
```bash
# Use -P solo flag for Windows
celery -A app.agents.executor worker --loglevel=info -P solo
```

---

## 📚 Next Steps

1. **Read the docs**: Check [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) for architecture details
2. **Explore agents**: See [backend/app/agents/](./backend/app/agents/) for agent implementations
3. **Try the API**: Use http://localhost:8000/api/docs to test endpoints
4. **Customize**: Modify agent behavior in the agent files
5. **Deploy**: See deployment guide for production setup

---

## 🆘 Need Help?

- **Documentation**: Check [SETUP.md](./SETUP.md) for detailed setup
- **Architecture**: See [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)
- **API Reference**: http://localhost:8000/api/docs
- **Issues**: Open an issue on GitHub

---

## 🎉 You're Ready!

Your Agentic AI Life Assistant is now running. Start by:

1. ✅ Creating your account
2. ✅ Setting up your first agent
3. ✅ Reviewing agent suggestions
4. ✅ Approving or rejecting tasks
5. ✅ Letting AI handle the rest!

**Enjoy your AI-powered productivity boost!** 🚀
