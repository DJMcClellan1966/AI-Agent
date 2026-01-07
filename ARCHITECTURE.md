# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                             │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              Next.js Frontend (Port 3000)                   │   │
│  │                                                              │   │
│  │  • Dashboard         • Agent Management                      │   │
│  │  • Task Approval     • Integrations                         │   │
│  │  • Settings          • Analytics                            │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
└────────────────────────────┬─┴──────────────────────────────────────┘
                             │
                             │ HTTPS / REST API
                             │
┌────────────────────────────▼──────────────────────────────────────┐
│                     API LAYER (FastAPI)                           │
│                                                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │   Auth     │  │   Users    │  │   Agents   │  │   Tasks    ││
│  │  Endpoints │  │  Endpoints │  │  Endpoints │  │  Endpoints ││
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘│
│                                                                    │
│  ┌────────────┐  ┌──────────────────────────────────────────┐   │
│  │Integration │  │     Security & Authentication             │   │
│  │ Endpoints  │  │     (JWT, OAuth2, Permissions)            │   │
│  └────────────┘  └──────────────────────────────────────────┘   │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
┌─────────────────▼─────────┐  ┌────────▼──────────────────────────┐
│   DATABASE LAYER          │  │     AGENT FRAMEWORK                │
│                           │  │                                    │
│  ┌────────────────────┐  │  │  ┌──────────────────────────────┐ │
│  │   PostgreSQL       │  │  │  │   Coordinator Agent           │ │
│  │                    │  │  │  │   (Orchestrates all agents)   │ │
│  │  • Users           │  │  │  └───────────────┬──────────────┘ │
│  │  • Agents          │  │  │                  │                 │
│  │  • Tasks           │  │  │     ┌────────────▼───────────┐    │
│  │  • Integrations    │  │  │     │   Specialized Agents   │    │
│  │  • Preferences     │  │  │     │                        │    │
│  └────────────────────┘  │  │     │  ┌──────────────────┐ │    │
│                           │  │     │  │   Email Agent    │ │    │
│  ┌────────────────────┐  │  │     │  │   • Sort emails   │ │    │
│  │      Redis         │  │  │     │  │   • Draft replies │ │    │
│  │                    │  │  │     │  └──────────────────┘ │    │
│  │  • Caching         │  │  │     │                        │    │
│  │  • Task Queue      │  │  │     │  ┌──────────────────┐ │    │
│  │  • Sessions        │  │  │     │  │ Scheduler Agent  │ │    │
│  └────────────────────┘  │  │     │  │ • Book meetings  │ │    │
└───────────────────────────┘  │     │  │ • Find times    │ │    │
                               │     │  └──────────────────┘ │    │
                               │     │                        │    │
                               │     │  ┌──────────────────┐ │    │
                               │     │  │  Finance Agent   │ │    │
                               │     │  │  • Track bills   │ │    │
                               │     │  │  • Negotiate     │ │    │
                               │     │  └──────────────────┘ │    │
                               │     └────────────────────────┘    │
                               │                                    │
                               │  ┌──────────────────────────────┐ │
                               │  │   LLM Integration             │ │
                               │  │                               │ │
                               │  │  • OpenAI (GPT-4)            │ │
                               │  │  • Anthropic (Claude)        │ │
                               │  │  • LangChain Framework       │ │
                               │  └──────────────────────────────┘ │
                               └────────────────────────────────────┘
                                              │
┌─────────────────────────────────────────────▼─────────────────────┐
│                    ASYNC TASK PROCESSING                           │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                    Celery Workers                             ││
│  │                                                                ││
│  │  • Execute agent tasks asynchronously                         ││
│  │  • Handle retries and failures                               ││
│  │  • Process scheduled tasks                                    ││
│  │  • Predict user needs                                         ││
│  └──────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                           │
│                                                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │   Gmail    │  │   Google   │  │   Stripe   │  │   Banks    │ │
│  │  /Outlook  │  │  Calendar  │  │  Payments  │  │    APIs    │ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Task Execution

```
1. User Creates Agent
   │
   ├──> Frontend sends POST /api/v1/agents/
   │
   └──> Backend creates Agent in database

2. Agent Analyzes Context
   │
   ├──> Agent reads user data (emails, calendar, etc.)
   │
   ├──> Uses LLM to analyze and suggest tasks
   │
   └──> Creates Task with status: AWAITING_APPROVAL

3. User Reviews Task
   │
   ├──> Frontend fetches tasks with status: AWAITING_APPROVAL
   │
   ├──> User sees task details and suggested action
   │
   └──> User clicks "Approve" or "Reject"

4. Task Execution
   │
   ├──> If approved: POST /api/v1/tasks/{id}/approve
   │
   ├──> Backend updates status to APPROVED
   │
   ├──> Celery worker picks up task
   │
   ├──> Agent executes the task
   │
   ├──> Uses LLM for complex decisions
   │
   ├──> Interacts with external APIs if needed
   │
   └──> Updates task status to COMPLETED or FAILED

5. Result Notification
   │
   └──> User sees updated task status on dashboard
```

## Agent Communication Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    Coordinator Agent                           │
│                                                                │
│  1. Receives multiple pending tasks                           │
│  2. Analyzes dependencies and conflicts                       │
│  3. Prioritizes based on user preferences                     │
│  4. Delegates tasks to specialized agents                     │
│  5. Monitors progress and resolves issues                     │
└────────────────────┬───────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
┌───────▼─────┐ ┌───▼──────┐ ┌──▼───────┐ ┌──▼───────┐
│   Email     │ │Scheduler │ │ Finance  │ │ Planning │
│   Agent     │ │  Agent   │ │  Agent   │ │  Agent   │
│             │ │          │ │          │ │          │
│  • Sort     │ │ • Book   │ │• Track   │ │• Plan    │
│  • Draft    │ │ • Find   │ │• Nego.   │ │• Opt.    │
│  • Follow   │ │ • Remind │ │• Save    │ │• Adapt   │
└─────────────┘ └──────────┘ └──────────┘ └──────────┘
       │              │            │            │
       └──────────────┴────────────┴────────────┘
                      │
              Report back to
              Coordinator
```

## Security Flow

```
1. User Registration/Login
   │
   ├──> Frontend: POST /api/v1/auth/register or /login
   │
   ├──> Backend: Validate credentials
   │
   ├──> Hash password with bcrypt
   │
   ├──> Create JWT access token (30 min expiry)
   │
   ├──> Create JWT refresh token (7 day expiry)
   │
   └──> Return tokens to frontend

2. Authenticated Request
   │
   ├──> Frontend: Include Bearer token in Authorization header
   │
   ├──> Backend: Verify JWT signature
   │
   ├──> Extract user_id from token
   │
   ├──> Load user from database
   │
   ├──> Check permissions for requested action
   │
   └──> Execute request or return 401/403

3. Token Refresh
   │
   ├──> If access token expired (401)
   │
   ├──> Frontend: Send refresh token to /api/v1/auth/refresh
   │
   ├──> Backend: Validate refresh token
   │
   ├──> Issue new access and refresh tokens
   │
   └──> Retry original request with new access token
```

## Subscription Flow

```
Free Tier
   │
   ├──> Limited to 2 agents
   ├──> 50 tasks/month
   └──> Manual approval required

User clicks "Upgrade"
   │
   ├──> POST /api/v1/subscriptions/upgrade
   │
   ├──> Backend creates Stripe Checkout session
   │
   ├──> User redirected to Stripe payment page
   │
   └──> After payment: Webhook updates subscription

Pro/Premium Tier
   │
   ├──> More agents enabled
   ├──> Higher task limits
   ├──> Autonomous execution allowed
   └──> Advanced features unlocked
```

## Docker Composition

```
┌──────────────────────────────────────────────────────────────┐
│                    Docker Network                             │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  postgres   │  │    redis    │  │   backend   │         │
│  │  Port: 5432 │  │  Port: 6379 │  │  Port: 8000 │         │
│  │             │  │             │  │             │         │
│  │  Database   │  │   Cache &   │  │  FastAPI    │         │
│  │   Storage   │  │    Queue    │  │    API      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                            │                 │
│                                            │                 │
│  ┌─────────────┐  ┌─────────────┐         │                 │
│  │   worker    │  │  frontend   │         │                 │
│  │             │  │  Port: 3000 │         │                 │
│  │  Celery     │  │             │         │                 │
│  │  Workers    │  │  Next.js    │◄────────┘                 │
│  │             │  │   App       │                           │
│  └─────────────┘  └─────────────┘                           │
└──────────────────────────────────────────────────────────────┘
         All containers share same network
         and can communicate by service name
```

## Technology Stack Summary

```
Frontend:
  ├── Next.js 14 (React framework)
  ├── TypeScript (Type safety)
  ├── Tailwind CSS (Styling)
  ├── React Query (Data fetching)
  └── Zustand (State management)

Backend:
  ├── FastAPI (Python web framework)
  ├── SQLAlchemy (ORM)
  ├── Pydantic (Data validation)
  ├── JWT (Authentication)
  └── Celery (Async tasks)

AI/ML:
  ├── OpenAI GPT-4 (Primary LLM)
  ├── Anthropic Claude (Alternative LLM)
  └── LangChain (Agent framework)

Database:
  ├── PostgreSQL (Primary database)
  └── Redis (Cache & queue)

Infrastructure:
  ├── Docker (Containerization)
  └── Docker Compose (Orchestration)
```
