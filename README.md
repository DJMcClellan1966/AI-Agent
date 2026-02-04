# Synthesis – Conversational App Creation & Agent

Create working web apps by describing them in plain language, and chat with an LLM-powered agent that can read files, edit code, and run commands (with your approval).

## ✨ Build (conversational apps)

- **Conversational UI**: Describe your app (e.g. "A habit tracker with streaks"), add more context in chat.
- **Real code generation**: Backend uses an LLM to turn the conversation into a structured spec, then generates `index.html`, `styles.css`, and `app.js`.
- **Download**: Get a zip of the generated files and run them locally.
- **Auth & projects**: Sign up, log in, and your generated projects are stored per user.

## 🤖 Agent (Cursor-like assistant)

- **Chat UI**: Use the **Agent** page to talk to an LLM that can call tools: `suggest_questions`, `generate_app`, `read_file`, `list_dir`, `edit_file`, `run_terminal`.
- **Human-in-the-loop**: File edits and terminal commands require your approval before they run.
- **Workspace**: Set an optional workspace root so the agent can read/edit files and run commands in your project.
- **Integrations (Cuddly-Octo)**: Toggle **CodeLearn** (guidance URL) and **CodeIQ** (workspace path) in the Agent Integrations panel. Settings are stored in the browser and can be prefilled from server defaults.

**Optional environment variables** (backend):

- `CODELEARN_GUIDANCE_URL` – Base URL for CodeLearn guidance (avoid/encourage patterns). UI can override via Integrations.
- `CODEIQ_WORKSPACE` – Default path for CodeIQ CLI (search_code, analyze_code). UI can override via Integrations.

See [docs/AGENT_ROADMAP.md](docs/AGENT_ROADMAP.md) for the roadmap and [docs/CUDDLY_OCTO_BENEFITS.md](docs/CUDDLY_OCTO_BENEFITS.md) for CodeLearn, CodeIQ, and Sentinel.

---

# AgenticAI – AI-Powered Life Assistant (legacy)

The codebase also includes an **Agentic AI Life Assistant** (multi-agent system for tasks, email, scheduling, etc.). That functionality is still available via API and code; the UI emphasizes **Build** instead.

## 🌟 Features

- **Multi-Agent System**: Specialized AI agents (Email, Scheduler, Finance, Planning, Coordinator) working together
- **Proactive Task Management**: Agents predict your needs and suggest actions before you ask
- **Permission-Based Actions**: Full user control with approval workflows
- **Email Management**: Smart email sorting, automated responses, and follow-up scheduling
- **Appointment Booking**: Automated scheduling with calendar integration
- **Bill Negotiation**: AI-powered negotiation for better rates on your services
- **Routine Planning**: Personalized daily/weekly routine optimization
- **Integration Hub**: Connect with Gmail, Outlook, Google Calendar, banking APIs, and more
- **Modern Dashboard**: Beautiful, responsive UI to monitor all agent activities
- **Subscription Tiers**: Free, Pro, and Premium plans with Stripe integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Frontend (Next.js 14)               │
│  - Modern Dashboard with Stats              │
│  - Agent Management & Configuration         │
│  - Task Approval Workflow                   │
│  - Integration Hub                          │
│  - Settings & User Profile                  │
│  - Subscription Management                  │
└─────────────┬───────────────────────────────┘
              │ REST API
┌─────────────▼───────────────────────────────┐
│      Backend API (FastAPI)                  │
│  - Authentication (JWT)                     │
│  - Agent CRUD & Orchestration               │
│  - Task Queue & Approval System             │
│  - Permission Manager                       │
│  - Subscription/Payment (Stripe)            │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│        Agent Framework (LangChain)          │
│  📧 Email Agent - Sort, draft, schedule     │
│  📅 Scheduler Agent - Book, optimize        │
│  💰 Finance Agent - Track, negotiate        │
│  📋 Planning Agent - Routines, priorities   │
│  🎯 Coordinator Agent - Orchestrate all     │
└─────────────────────────────────────────────┘
```

## 🚀 Tech Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL** for data storage
- **Redis** for caching and task queues
- **Celery** for async task processing
- **OpenAI/Anthropic APIs** for AI capabilities
- **LangChain** for agent orchestration

### Frontend
- **Next.js 14+** with App Router
- **TypeScript**
- **Tailwind CSS** for styling
- **Shadcn/UI** for components
- **React Query** for data fetching
- **Zustand** for state management

### Infrastructure
- **Docker** & Docker Compose
- **Nginx** for reverse proxy
- **PostgreSQL** database
- **Redis** for caching

## 📋 Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd AI-Agent
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 4. Database Setup
```bash
# Using Docker
docker-compose up -d postgres redis

# Run migrations
cd backend
alembic upgrade head
```

### 5. Run the Application

**Using Docker (Recommended):**
```bash
docker-compose up
```

**Manual:**
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Worker
cd backend
celery -A app.worker worker --loglevel=info
```

Access the application at `http://localhost:3000`

## 🎯 Usage

1. **Sign Up**: Create your account
2. **Connect Services**: Link email, calendar, and other services
3. **Configure Agents**: Set preferences for each agent
4. **Set Permissions**: Define what agents can do automatically
5. **Monitor Dashboard**: Track agent activities and approve actions

## 🤖 Agent Types

### Email Agent
- Sorts and categorizes emails
- Drafts responses
- Schedules follow-ups
- Flags urgent messages

### Scheduler Agent
- Books appointments
- Finds optimal meeting times
- Reschedules conflicts
- Sends reminders

### Finance Agent
- Tracks bills
- Negotiates with service providers
- Finds better rates
- Monitors spending

### Planning Agent
- Optimizes daily routines
- Suggests task prioritization
- Plans weekly schedules
- Adapts to patterns

### Coordinator Agent
- Manages inter-agent communication
- Resolves conflicts
- Prioritizes tasks
- Learns user preferences

## 💰 Subscription Tiers

### Free Tier
- Basic email management
- Manual appointment booking
- Limited to 50 tasks/month

### Pro ($10/month)
- All agents enabled
- 500 tasks/month
- Basic integrations
- Email support

### Premium ($30/month)
- Unlimited tasks
- Advanced integrations
- Priority support
- Custom agent training
- White-label options

## 🔐 Security & Privacy

- End-to-end encryption for sensitive data
- OAuth 2.0 for service integrations
- User consent required for all actions
- Data retention policies
- GDPR compliant

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📚 Documentation

- [Agent roadmap & tools](docs/AGENT_ROADMAP.md)
- [Cuddly-Octo (CodeLearn, CodeIQ, Sentinel)](docs/CUDDLY_OCTO_BENEFITS.md)
- [Architecture](ARCHITECTURE.md) · [Quickstart](QUICKSTART.md) · [Setup](SETUP.md)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details

## 🆘 Support

- Email: support@agentic-ai.app
- Documentation: https://docs.agentic-ai.app
- Discord: https://discord.gg/agentic-ai

## 🗺️ Roadmap

- [ ] Voice agent integration
- [ ] Mobile app (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] Custom agent marketplace
- [ ] Team collaboration features
- [ ] Smart home integrations
