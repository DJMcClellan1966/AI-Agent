# How CodeLearn, CodeIQ, and Sentinel Can Benefit Synthesis / Your Agent

This doc summarizes what each **cuddly-octo-computing-machine** component does and how it could add benefit to the Synthesis app and your agent.

---

## 1. CodeLearn

**What it is:** A learning loop that connects **code patterns** (from commits/CodeIQ) with **outcomes** (e.g. production anomalies from Sentinel). It maintains a pattern DB, risk scores, co-occurrence, “hub” patterns, and temporal trends. It exposes a **guidance API** (avoid/encourage) and **suggest** (LLM or template fix suggestions for a pattern).

**What could benefit Synthesis/agent:**

| Idea | Benefit |
|------|--------|
| **Guidance in the agent** | When your agent generates code (or suggests edits), call CodeLearn’s `/guidance` (or `/v1/guidance`) and inject “Avoid: …”, “Encourage: …” into the system prompt. Generated code then tends to follow learned best practices and avoid patterns that historically correlated with issues. |
| **Suggest after generate** | After Synthesis generates HTML/CSS/JS, run a lightweight “pattern scan” on the generated code (e.g. simple rules: no `eval`, no inline secrets, no bare `catch`). Map findings to CodeLearn pattern names and call `/suggest` to get human-readable fix suggestions; show them in the UI as “Suggested improvements.” |
| **Compound risk for projects** | If you track “which patterns appear in this generated project,” you can call CodeLearn’s `/score` with those patterns and show a “Code quality risk” indicator (e.g. “Low / Medium / High”) so users know when to review the output more carefully. |
| **Pre-commit / CI for generated code** | If users commit generated code to a repo, CodeLearn’s pre-commit hook or CI integration can warn when risky patterns are introduced—same flow as hand-written code. |

**Integration effort:** Medium. CodeLearn runs as a separate service (Flask). Your backend would call it over HTTP (e.g. `GET /guidance`, `POST /suggest`) or you embed the pattern DB + kernel in your app and call them in-process. Easiest: call the existing CodeLearn API from your agent kernel before/after `generate_app`.

---

## 2. CodeIQ

**What it is:** Code analysis over a codebase: **indexer** (AST/entity extraction for Python, regex for JS/TS), **analyzer** (duplicates, issues, patterns, complexity, dependencies, circular imports). It supports **semantic search** (“find code by meaning”), duplicate detection, similar-code finder, and complexity metrics (cyclomatic, maintainability index).

**What could benefit Synthesis/agent:**

| Idea | Benefit |
|------|--------|
| **“Understand this codebase” before acting** | When the user sets a `workspace_root`, run CodeIQ’s indexer on it. Your agent then has a **search** tool: “search code: &lt;query&gt;” that calls CodeIQ’s semantic/search API. The agent can answer “where is auth handled?” or “what calls this function?” using real code structure instead of only raw file content. |
| **Analyze generated output** | After Synthesis generates a project, write the files to a temp dir and run CodeIQ’s analyzer (issues, duplicates, complexity). Show a short report in the UI: “Generated code: 3 issues (e.g. long function), 0 duplicates, complexity B.” Gives users and the agent a quality signal. |
| **Agent tool: find_similar_code** | Add an agent tool that calls CodeIQ’s “similar to function X” or “duplicates.” The agent can suggest “there’s code similar to this in `other_file.py`—consider refactoring.” |
| **Dependency / circular view** | For workspace-aware agent sessions, “show deps” or “find circular imports” (CodeIQ) helps the agent reason about impact of edits. |

**Integration effort:** Medium. CodeIQ is Python (indexer, analyzer, parser); you can run it as a subprocess or import it. Easiest: add a **tool** in your agent kernel that runs CodeIQ’s indexer on `context["workspace_root"]` and then runs search or analyze; return a short summary to the LLM.

---

## 3. Sentinel

**What it is:** Real-time **anomaly detection** on event streams: numeric outliers, rare categories, rate anomalies, new patterns. It has a REST API for ingestion, SQLite persistence, alerts (console, webhook, Slack), and optional ML scoring. CodeLearn’s **correlator** can read Sentinel’s DB and link anomalies to recent commits/patterns.

**What could benefit Synthesis/agent:**

| Idea | Benefit |
|------|--------|
| **Monitor generated or deployed apps** | If users run their Synthesis-generated app (or any app) and send metrics/events (e.g. response times, errors) to Sentinel, Sentinel detects anomalies. You don’t change Synthesis itself; you offer “optional: send your app’s metrics to our Sentinel endpoint” for users who want monitoring. |
| **“What might have caused this?” in the agent** | When Sentinel fires an alert, CodeLearn’s correlator can suggest “these commits/patterns might be related.” In an agent UI you could add a card: “Recent anomaly in stream X — possible causes: [list from correlator].” That’s more relevant for **hand-written** repos with commits; for **generated** projects you could still correlate by “last time this project was regenerated” or “last edit.” |
| **Feedback loop for generated code** | If you store “this project was generated from this spec” and later Sentinel reports anomalies for an app built from that project, you could (long-term) feed that back into CodeLearn as outcomes and gradually learn “specs that lead to pattern X tend to get anomalies.” Then the agent could warn or suggest alternatives when generating similar specs. |

**Integration effort:** Medium–high. Sentinel runs as its own service (Flask + SQLite). You could: (1) run Sentinel as a sidecar and have users’ apps POST events to it; (2) add an optional “Send events to Sentinel” in your backend when users run/preview generated apps; (3) periodically run CodeLearn’s correlator against Sentinel’s DB and expose “recent anomalies + suspected causes” in the dashboard or agent.

---

## Summary table

| Component   | Best benefit for Synthesis/agent                          | Effort |
|------------|-----------------------------------------------------------|--------|
| **CodeLearn**  | Guidance (avoid/encourage) in agent prompt; suggest fixes for generated code; compound risk score for projects. | Medium (HTTP or embed kernel) |
| **CodeIQ**     | Workspace-aware agent: semantic search, analyze generated code, find similar/duplicates, deps.              | Medium (subprocess or import + tools) |
| **Sentinel**   | Monitor generated or deployed apps; correlate anomalies with “what changed”; optional feedback into learning. | Medium–high (separate service + optional correlation) |

---

## Suggested order

1. **CodeLearn guidance** – Call `/guidance` (or kernel’s `get_guidance`) when the agent is about to generate code; add “Avoid: …, Encourage: …” to the system prompt. Low surface area, immediate improvement in generated code quality.
2. **CodeIQ search + analyze** – Add agent tools: `search_code(query)` and `analyze_code(path)` using CodeIQ on `workspace_root`. Enables “understand this repo” and “analyze this generated project.”
3. **CodeLearn suggest** – After generate (or in a “Review” step), run a simple pattern scan on generated files, map to CodeLearn pattern names, call `/suggest`, show suggestions in the UI.
4. **Sentinel (optional)** – If you want “monitor my app” or “what caused this alert,” add Sentinel as an optional service and, if useful, wire CodeLearn’s correlator so the agent or dashboard can show “recent anomalies and suspected causes.”

This keeps Synthesis/agent as the core and uses cuddly-octo as **optional quality and observability layers** you can plug in step by step.

---

## Env vars used by this app (when integrating cuddly-octo)

| Variable | Used by | Purpose |
|----------|---------|--------|
| `CODELEARN_GUIDANCE_URL` | Agent kernel | Base URL of CodeLearn guidance API (e.g. `http://localhost:5050`). Agent system prompt gets "Avoid / Encourage" from `GET /guidance`. |
| `CODEIQ_WORKSPACE` | Agent kernel | Path to a directory that has been indexed with CodeIQ (or that you run CodeIQ from). Enables `search_code` and `analyze_code` tools. Ensure `codeiq` is on `PYTHONPATH` (e.g. add cuddly-octo repo root) so `python -m codeiq.cli search ...` works. |
