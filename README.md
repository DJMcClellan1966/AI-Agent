# Local Agent IDE

A simple IDE + Opus-like agent: file tree, editor, and chat with an LLM (Ollama qwen3:8b by default) that can read files, edit code, run commands, and generate apps—with your approval.

## What’s in the app

- **IDE** (`/ide`): Workspace root, file tree, file viewer, and agent chat in one screen.
- **Agent** (`/agent`): Full chat with the same agent (workspace, approve edits/commands). Uses Opus-like prompting (reasoning, JSON-only).
- **Build** (`/build`): Describe an app in chat → get a single HTML file (Synthesis-style) to open in the browser.
- **Auth**: Login/register and settings. No payments or external integrations.

## Run locally (no API keys)

1. **Ollama**: Install [Ollama](https://ollama.ai), then `ollama pull qwen3:8b`.
2. **Backend**: Copy `.env.example` to `.env` (use `DATABASE_URL=sqlite:///./agentic_ai.db`, `USE_CELERY=false`). Start: `uvicorn app.main:app --reload --port 8001` (from `backend/` with venv active).
3. **Frontend**: `cd frontend && npm install && npm run dev`.
4. Or from project root: `.\run-simple.ps1` (starts backend in a new window, then frontend).

Open http://localhost:3000. In the IDE, set **Workspace root** to a folder path so the agent can read/edit files and run commands.

## Guide docs (this repo)

- [docs/AGENT_ROADMAP.md](docs/AGENT_ROADMAP.md) – Agent kernel, tools, roadmap.
- [docs/COMPARISON_AND_IMPROVEMENTS.md](docs/COMPARISON_AND_IMPROVEMENTS.md) – How this compares to Cursor, Synthesis, etc.
- [docs/CUDDLY_OCTO_BENEFITS.md](docs/CUDDLY_OCTO_BENEFITS.md) – CodeIQ/CodeLearn ideas (reference; integration code removed for simplicity).
- [docs/DESKTOP_CODE_FINDINGS.md](docs/DESKTOP_CODE_FINDINGS.md) – Desktop/code findings.
- [docs/LOCAL_AGENT_IDE.md](docs/LOCAL_AGENT_IDE.md) – Local Agent IDE setup and usage.
- [docs/ML_TOOLBOX_BENEFITS.md](docs/ML_TOOLBOX_BENEFITS.md) – ML toolbox ideas (reference).
- [docs/OPUS_LIKE_AGENT.md](docs/OPUS_LIKE_AGENT.md) – Opus-like behavior with open-source models.

See [SETUP.md](SETUP.md) for detailed setup (including simplified run and Docker).
