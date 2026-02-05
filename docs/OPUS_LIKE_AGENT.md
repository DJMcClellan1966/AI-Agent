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

## Can You Modify an Open-Source Model?

**You don’t have to.** For an Opus-like agent, use an open-source model **as-is** with:

- `USE_LOCAL_LLM=True` and `LOCAL_MODEL_NAME=<model>` (e.g. in Ollama)
- `agent_style=opus_like` in context

The behavior comes from the **system prompt and tool loop**, not from changing the model’s weights.

**If you want to “modify” a model (fine-tune):**

- **What it is:** Train or adapt the model on your own data (e.g. tool-calling examples, coding Q&A) so it’s better at JSON output and reasoning in your format.
- **What you need:** A dataset (input/output pairs), GPU(s), and a pipeline (e.g. LoRA/QLoRA with Hugging Face, or Ollama’s Modelfile for light customization). This is a separate ML project, not a config change in this app.
- **When it’s worth it:** If you’ve already picked a strong base model and still see consistent failures (e.g. wrong tool names, ignoring “JSON only”). Start with a good base model + Opus-like prompt; consider fine-tuning only if you hit clear limits.

---

## Recommended Open-Source Models for the Opus-like Agent

Use one of these **without modifying weights**; run via **Ollama** (this app’s default local backend) and set `agent_style=opus_like`.

| Model (Ollama name) | Best for | VRAM / RAM | Notes |
|--------------------|----------|------------|--------|
| **qwen2.5:7b** | Balanced quality/speed, JSON and tools | ~8 GB | Strong instruction following and JSON; good default. |
| **qwen3:8b** | Newer Qwen 3, instruction + tools | ~8 GB | Good alternative to 2.5:7b; use if you have it. |
| **qwen2.5:14b** | Better reasoning, still single-GPU | ~16 GB | More reliable tool choice and “thought” than 7B. |
| **llama3.1:8b** | General chat + tools | ~8 GB | Solid; slightly less code-focused than Qwen. |
| **llama3.1:70b** | Closest to “Opus-like” reasoning | ~48 GB+ | Best quality if you have the hardware. |
| **deepseek-coder:6.7b** | Code-heavy tasks (read_file, edit_file, suggest_fix) | ~8 GB | Optimized for code; good for coding-agent use. |
| **mistral:7b** | Fast, lightweight | ~8 GB | Good fallback; may need stricter prompting for JSON. |
| **phi3:medium** | Lower resource | ~8 GB | Smaller; use if 7B is too heavy. |

**Recommendation:**

- **Default choice:** **Qwen 2.5 7B** (`qwen2.5:7b`) or **Qwen 3 8B** (`qwen3:8b`) – both work well with the Opus-like prompt; use whichever you have (e.g. `ollama list`).
- **More “Opus-like” quality:** **Qwen 2.5 14B** or **Llama 3.1 70B** if you have the GPU/RAM.
- **Code-focused agent:** **DeepSeek Coder 6.7B** for read_file / edit_file / suggest_fix–heavy use.

**Setup (no model modification):**

1. Install [Ollama](https://ollama.com) and pull a model, e.g.:
   ```bash
   ollama pull qwen2.5:7b
   ```
2. In the backend `.env` (use a model you’ve pulled, e.g. `qwen2.5:7b` or `qwen3:8b`):
   ```env
   USE_LOCAL_LLM=true
   LOCAL_LLM_BACKEND=ollama
   LOCAL_MODEL_NAME=qwen2.5:7b
   ```
   Or set `LOCAL_MODEL_NAME=qwen3:8b` if you prefer Qwen 3 8B.
3. Use the agent with Opus-like style (API or CLI):
   - API: `context.agent_style = "opus_like"`
   - CLI: `python -m app.agent_cli --agent-style opus_like --workspace .`

No code changes to the model; the Opus-like behavior comes from **model choice + `agent_style=opus_like` + your existing tools**.

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
