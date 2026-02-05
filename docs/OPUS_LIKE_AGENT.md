# Building an Agent That Works Like Opus (Without Using Opus)

You want your app’s agent to **behave** like Claude Opus—thoughtful, reliable tool use, clear reasoning—without necessarily calling the Opus API. This doc explains what’s open source, what isn’t, and how to shape your agent to feel “Opus-like.”

---

## Is Opus Open Source?

**No.** Claude Opus is Anthropic’s **proprietary** model. You cannot:

- Download or self-host Opus
- Run it fully offline
- Use it without the Anthropic API (and their terms/pricing)

There is no open-source “Opus.” What you *can* do is:

1. **Use your current stack** (any LLM: OpenAI, Anthropic, or **local/open-source**) and design your **agent** (prompts, loop, tools) so it **behaves** in an Opus-like way.
2. Use **open-source models** (Llama, Mistral, Qwen, DeepSeek, etc.) via Ollama or your backend and get “good agent behavior” by **architecture and prompting**, not by the model being Opus.

So: **Opus is not open source; an “Opus-like” agent is something you build** with the right design and, if you want, open-source models.

---

## What Makes Opus “Feel” the Way It Does?

Opus is known for:

- **Reasoning before acting** – brief “thought” before each tool call or reply
- **Reliable tool use** – picks the right tool and args, follows the schema
- **Conciseness** – avoids long rambles; gets to the point
- **Multi-step planning** – uses several tools in sequence when needed
- **Staying on instruction** – follows “reply with JSON only,” “be concise,” etc.

You can approximate that with **any** capable model by:

1. **System prompt** – explicit role, tool rules, and output format
2. **Structured output** – JSON with `thought` + `tool`/`reply` (you already have this)
3. **Tool descriptions** – clear, one-purpose descriptions (you have this)
4. **Context** – workspace, guidance, and conversation in the prompt (you have this)
5. **Model choice** – better models follow instructions and reason more reliably

---

## How to Make Your Agent More “Opus-Like”

### 1. Strengthen the system prompt (reasoning + discipline)

Your kernel already uses a `thought` field. Make the system prompt explicitly ask for **short reasoning before every action** and **strict JSON**. For example, in `agent_kernel.py` you can use a more Opus-style system block:

- **Role:** “You are a precise coding and product assistant. Think step-by-step, then act.”
- **Output rule:** “Always output valid JSON only. No markdown, no explanation outside JSON.”
- **Reasoning:** “Before calling a tool or replying: state in one sentence what you’re doing and why (in the ‘thought’ field).”
- **Conciseness:** “Keep replies and thoughts short. Prefer one tool call per step when possible.”

You can make this **configurable** (e.g. `context.agent_style = "opus_like"`) so you can switch between a minimal prompt and this stricter, Opus-like one.

### 2. Keep your existing architecture

Your loop is already Opus-friendly:

- Tools are well-named and single-purpose
- You require JSON with `thought` and either `tool`+`args` or `reply`
- You have workspace context, optional semantic context, and optional CodeLearn guidance
- Human-in-the-loop for edits and terminal keeps behavior controlled

No need to change the loop; **tuning the system prompt and (optionally) the per-turn prompt** is enough to get most of the “Opus-like” feel.

### 3. Optional: “Agent style” in context

Add a simple notion of **agent style** so you can switch behaviors without editing code:

- **Default** – current short system prompt
- **opus_like** – longer system prompt that stresses: one-sentence reasoning, JSON-only, one step at a time, concise replies

Then in the API or CLI, pass `context.agent_style = "opus_like"` when you want that behavior. The same code and same tools work; only the system text changes.

### 4. Model choice (if you want “Opus-like” with open source)

If you’re not using the Opus API, the closest you can get with **open-source** is to use a strong local model and the same prompt/loop:

- **Via Ollama (you already support local LLM):** e.g. `llama3.1:70b`, `mistral:latest`, `qwen2.5:72b`, `deepseek-coder` (for code-heavy tasks). Set `USE_LOCAL_LLM=True` and `LOCAL_MODEL_NAME` to the model you want.
- **Not open source but self-hosted:** e.g. run a licensed model on your own GPU (many vendors offer this). Your agent code stays the same; you just point `_get_llm()` at that backend.

“Opus-like” here comes from **prompt + loop + tool design**, not from the model being open source. A good open-source model with your Opus-style prompt will behave much closer to what you want than a weak model with the same prompt.

---

## Summary

| Question | Answer |
|----------|--------|
| Is Opus open source? | **No.** It’s Anthropic’s proprietary API model. |
| Can I build an agent that *works like* Opus? | **Yes.** By prompt design (reasoning, JSON-only, concise) and your existing tool loop. |
| Can I use open-source models for that? | **Yes.** Use your current local LLM path (e.g. Ollama) with a capable model and the same “Opus-like” system prompt. |
| What to change in this app? | Prefer **system prompt** (and optional “agent style”) first; keep your architecture and tools as they are. |

---

## How to Enable “Opus-like” in This App

The agent kernel supports **`agent_style`** in `context`:

- **API (POST /api/v1/agent/chat):** Send `context.agent_style = "opus_like"` in the request body:
  ```json
  {
    "messages": [...],
    "context": { "workspace_root": "/path/optional", "agent_style": "opus_like" }
  }
  ```
- **CLI:** From the backend directory run: `python -m app.agent_cli --agent-style opus_like [--workspace PATH]`. Same context is passed to the kernel.

With `agent_style: "opus_like"`, the system prompt stresses: one-sentence reasoning in `thought`, JSON-only output, one step at a time, and concise replies. Works with **any** model (OpenAI, Anthropic, or local).
