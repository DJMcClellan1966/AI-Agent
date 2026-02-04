# Your Own Agent (Like Cursor / Auto): Roadmap & Ideas

This doc is about turning **Synthesis** into a **starting point for your own coding/productivity agent**—something that can chat, use tools, and act on your behalf (with your approval).

---

## Can This Be the Starting Point?

**Yes.** You already have:

- **Conversational UI** (Build page) and auth
- **LLM integration** (OpenAI, Anthropic, local) and a pattern of “prompt → parse → act”
- **Structured actions** (suggest questions, conversation → spec, spec → code)
- **Backend that can run arbitrary Python** (so adding “tools” is natural)

What’s missing to feel “like an agent” is:

1. **Tools** – e.g. read file, edit file, run command, search code, search web
2. **Agent loop** – LLM decides “call tool X with args Y” → you execute → return result → LLM continues or replies
3. **Context** – workspace path, current file, optional codebase index so the agent “sees” your project
4. **Control** – human-in-the-loop (approve edits/commands) vs autonomous mode

The roadmap below turns this repo into that starting point step by step.

---

## Path 1: Add an Agent Kernel (Recommended First Step)

**Idea:** Introduce a single **agent kernel** that:

- Keeps a **conversation** (messages) and optional **context** (e.g. workspace root, current file).
- Has a **tool registry**: each tool has a name, description, and a function `(args) -> result`.
- Runs a **loop**: send conversation + tool list to the LLM; if it returns a tool call, run the tool, append result to the conversation, repeat; otherwise return the final reply to the user.

Then:

- **Build (Synthesis)** becomes one use case: a pre-defined flow that uses “suggest_question”, “conversation_to_spec”, “spec_to_code” (as tools or as a single high-level tool).
- A new **Agent** tab (or CLI) uses the same kernel with **code tools**: e.g. `read_file`, `edit_file`, `run_terminal`, `grep`, `list_dir`. That’s “your own agent like Cursor.”

**Concrete steps:**

1. **Phase 1 – Kernel only (no new UI)**  
   - Add `AgentKernel` (or `AgentRunner`): `run(messages, context, tools) -> (messages, final_text)`.  
   - Tools are functions; you pass a list of `{ "name", "description", "function" }`.  
   - LLM prompt: “You have these tools. Reply with JSON: either `{"thought": "...", "tool": "name", "args": {...}}` or `{"thought": "...", "reply": "..."}` to finish.”  
   - Execute the tool, append `Assistant used tool X: <result>` to messages, call LLM again.  
   - Add one endpoint, e.g. `POST /api/v1/agent/chat` with `{ "messages", "context": { "workspace_root?" } }`, that runs this loop and returns the updated messages + final reply.

2. **Phase 2 – Register real tools**  
   - `read_file(path)` – read from `workspace_root` (or a sandbox dir).  
   - `list_dir(path)` – list directory.  
   - `search_files(pattern, path)` – grep/search in workspace.  
   - `edit_file(path, old_string, new_string)` or `patch_file(path, patch)` – propose an edit; optionally require approval before applying.  
   - `run_terminal(command, cwd)` – run in sandbox; stream or return stdout/stderr.  
   - Keep **Build** as a composite tool: `generate_app(messages)` that calls your existing `conversation_to_spec` + `spec_to_code` and returns project.

3. **Phase 3 – UI and control**  
   - New **Agent** page: chat input + message list. When the kernel wants to call a tool, show “Agent wants to: read_file('src/foo.ts'). Allow?” and only append the result after approval (or add “Autonomous” toggle).  
   - Optional: show diffs for `edit_file` before applying.

This gives you a single codebase where “Synthesis” is one agent mode and “Code Agent” is another, both using the same kernel and auth.

---

## Path 2: Workspace-Aware + Codebase Index

- Let the user set a **workspace root** (e.g. path on server, or upload a zip / connect to a repo).
- **Index** the codebase (e.g. embeddings or simple keyword index) so the agent can “search for relevant code” and get snippets as context.
- In the agent prompt, inject “Relevant snippets: …” so it can refer to the user’s actual files.  
This is the “outside-the-box” upgrade that makes the agent feel like it “understands” the project.

---

## Path 3: Multiple Interfaces (Same Agent)

- **Web (current)** – Build + Agent tabs.
- **CLI** – e.g. `python -m app.agent_cli` that runs the same kernel in the terminal (stdin/stdout); useful for scripting and power users.
- **Slack/Discord bot** – same backend, new route that receives webhooks and pushes replies back. One agent, many surfaces.

---

## Path 4: “Recipes” and Custom Behavior

- **Recipes** = named flows: “When user says ‘refactor this’, run: read_file → suggest_edits (LLM) → show diff → apply if user approves.”  
- Stored as config or simple scripts that call the kernel with a fixed tool sequence.  
- Lets you define “my own agent’s personality” (e.g. always run tests after edit, or always suggest a one-line summary).

---

## Outside-the-Box Ideas

| Idea | What it is | Why it’s interesting |
|------|------------|----------------------|
| **Voice in/out** | Speech-to-text for input, TTS for reply | Feels like a pair programmer you talk to. |
| **Human-in-the-loop by default** | Every tool call (edit, run) requires approval; “Autonomous” is opt-in. | Trust and safety from day one. |
| **Codebase embeddings** | Index repo with sentence-transformers; “relevant snippets” in context. | Agent can answer “where do we handle auth?” from your code. |
| **Multi-agent** | Coordinator agent that delegates to “code”, “docs”, “test” agents (each with different tools/prompts). | You already had Coordinator; reuse it as the “brain” and give it sub-agents with tools. |
| **Agent recipes** | User-defined flows: “when I say X, do Y and Z.” | Custom behavior without changing core code. |
| **Local-first SDK** | Package the kernel + tools as a library; run from CLI or a minimal UI. | “My own agent” runs on your machine, no server required. |

---

## Suggested Order of Work

1. **Implement the agent kernel** (Phase 1 above) and a single `POST /agent/chat` (or `/agent/run`) that runs the loop with a small set of tools (e.g. `suggest_question`, `generate_app`, and one or two placeholders like `read_file`).  
2. **Add real code tools** (`read_file`, `list_dir`, `edit_file`, `run_terminal`) with a configurable `workspace_root`.  
3. **Add an Agent chat UI** that calls the kernel and shows tool-call approval when needed.  
4. **Optional:** Codebase index (embeddings or search) and inject “relevant snippets” into the agent context.  
5. **Optional:** CLI and/or Slack/Discord so the same agent runs from terminal or chat.

---

## Summary

- **Yes**, this repo can be the starting point for “your own agent like me.”
- **Best next step:** add an **agent kernel** (LLM + tool loop + one endpoint), then register **code tools** and an **Agent** tab with human-in-the-loop.
- **Upgrades:** workspace awareness, codebase index, recipes, multi-agent, voice, multiple interfaces.

---

## Implemented: Phase 1 kernel + endpoint

In this repo you now have:

- **`backend/app/services/agent_kernel.py`** – `run_loop(messages, context, tools, max_turns)` runs the LLM in a loop; the model can output either a tool call (JSON with `tool` + `args`) or a final `reply`. Built-in tools:
  - `suggest_questions` – uses your existing suggest_questions (conversation → 1–2 questions).
  - `generate_app` – uses conversation_to_spec + spec_to_code (no DB save; caller can persist).
  - `read_file` – reads from `context.workspace_root` (returns error if not set).
  - `list_dir` – lists a directory under `workspace_root`.
- **`POST /api/v1/agent/chat`** – body: `{ "messages": [ { "role", "content" } ], "context": { "workspace_root": "/optional/path" } }`. Returns `{ "reply": "...", "messages": [ ... ] }`.

**How to try it:** Call the endpoint with a single user message, e.g. “I want a habit tracker.” The agent can call `suggest_questions` or `generate_app` and then reply. Set `context.workspace_root` to a directory path (on the server) to try `read_file` / `list_dir`.

**Next steps for you:** Add an “Agent” chat UI that calls this endpoint; add tools like `edit_file` and `run_terminal` with human-in-the-loop (show proposed edit or command, confirm before running).
