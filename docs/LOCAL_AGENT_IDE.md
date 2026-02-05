# Local Agent IDE

This app is trimmed to a **local agent IDE** (VSCode/Cursor/Synthesis-style): one Opus-like agent (Ollama qwen3:8b), file tree, editor, and chat. No cloud API keys, no subscriptions, no multi-agent task queue.

## What’s included

- **IDE** (`/ide`): Workspace root, file tree, file viewer, and agent chat in one layout. Set a folder path so the agent can read/edit files and run commands.
- **Agent** (`/agent`): Full chat with the same agent (workspace, edit/run approval, optional CodeLearn/CodeIQ). Default style: **opus_like** (reasoning + JSON-only + concise).
- **Build** (`/build`): Conversational app generation (Synthesis-style single HTML).
- **Auth**: Login/register and settings. No Stripe or integrations.

## Backend (simplified)

- **Routers**: `auth`, `users`, `workspace` (list/read for IDE), `agent` (chat + execute-pending), `build`.
- **Removed**: `agents`, `tasks`, `integrations`, `subscriptions` (no multi-agent CRUD, no Celery task queue, no payments).
- **Workspace API**: `GET /api/v1/workspace/list?root=&path=` and `GET /api/v1/workspace/read?root=&path=` for the IDE file tree and editor. Same path rules as the agent (`WORKSPACE_ALLOWED_ROOTS` if set).

## Run locally (no API keys)

1. **Ollama**: Install [Ollama](https://ollama.ai), then:
   ```bash
   ollama pull qwen3:8b
   ```
2. **Backend `.env`** (in repo root or `backend/`):
   ```env
   USE_LOCAL_LLM=true
   LOCAL_LLM_BACKEND=ollama
   LOCAL_MODEL_NAME=qwen3:8b
   DATABASE_URL=sqlite:///./agentic_ai.db
   USE_CELERY=false
   ```
   Leave `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` empty.
3. **Start**: Backend (`uvicorn app.main:app --reload --port 8001`), then frontend (`npm run dev`). Or use `.\run-simple.ps1` from project root.
4. **IDE**: Open the app, go to **IDE**, set **Workspace root** to an absolute path (e.g. `C:\Users\You\myproject`). The agent uses this for `read_file`, `edit_file`, `run_terminal`, etc.

## Opus-like behavior

- **Context**: The frontend sends `agent_style: "opus_like"` so the kernel uses the stricter system prompt (one-sentence reasoning, JSON-only, one step at a time).
- **Model**: qwen3:8b via Ollama is the default; you can change `LOCAL_MODEL_NAME` to another model (e.g. `qwen2.5:7b`, `deepseek-coder:6.7b`). See `docs/OPUS_LIKE_AGENT.md`.

## Optional: restrict workspace paths

To limit which folders the IDE and agent can access, set in `.env`:

```env
WORKSPACE_ALLOWED_ROOTS=C:\Users\You\projects,D:\dev
```

Then only paths under those roots are allowed for `workspace_root` and for agent tools.
