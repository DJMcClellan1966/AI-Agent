# Agentic AI Life Assistant

A proactive AI agent system that autonomously handles daily tasks including booking appointments, negotiating bills, managing emails, and planning routines using interconnected AI agents.

## 🌟 Features

- **Multi-Agent System**: Specialized AI agents working together
- **Proactive Task Management**: Agents predict needs and suggest actions
- **Permission-Based Actions**: User control over agent actions
- **Email Management**: Smart email sorting, responses, and follow-ups
- **Appointment Booking**: Automated scheduling with calendar integration
- **Bill Negotiation**: AI-powered negotiation for better rates
- **Routine Planning**: Personalized daily/weekly routine optimization
- **Integration Hub**: Connect with calendars, email, banking, and more

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Next.js)              │
│  - Dashboard                            │
│  - Agent Management                     │
│  - Task Approval UI                     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│      Backend API (FastAPI)              │
│  - Agent Orchestrator                   │
│  - Task Queue                           │
│  - Permission Manager                   │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│        Agent Framework                  │
│  - Email Agent                          │
│  - Scheduler Agent                      │
│  - Finance Agent                        │
│  - Planning Agent                       │
│  - Coordinator Agent                    │
└─────────────────────────────────────────┘
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

- [API Documentation](./docs/api.md)
- [Agent Development Guide](./docs/agents.md)
- [Integration Guide](./docs/integrations.md)
- [Deployment Guide](./docs/deployment.md)

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
