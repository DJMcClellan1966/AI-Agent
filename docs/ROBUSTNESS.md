# Making the App More Robust

This doc outlines patterns and improvements for reliability, safety, and operability. Use it as a checklist and reference.

---

## 1. Input Validation & Limits

**Why:** Unbounded input can cause OOM, slow LLM calls, or abuse.

**Done / in place:**
- Pydantic schemas validate types and required fields.
- Agent kernel: `_safe_path()` blocks path traversal; subprocess timeout (e.g. 60s) for `run_terminal`.
- Builder: `build_conversation_summary()` caps length; JSON extraction is bounded.

**Recommendations:**
- **Message limits:** Cap `messages` length and per-message `content` length in agent chat and build (e.g. max 50 messages, 50KB per content). Return 400 with a clear message when exceeded.
- **Request body size:** Use FastAPI/Starlette request size limits or a reverse proxy limit (e.g. 1MB for JSON) to avoid huge payloads.
- **Workspace path:** Ensure `context.workspace_root` is validated server-side (path exists, under allowed roots) before passing to tools.

---

## 2. Error Handling

**Why:** Consistent errors and logging make debugging and client handling easier.

**Done / in place:**
- Global `Exception` handler in `main.py` returns 500 and logs with `exc_info=True`.
- Services use try/except and return structured JSON (e.g. `{"error": "..."}`) from tools.
- FastAPI returns 422 for Pydantic validation errors.

**Recommendations:**
- **Validation error handler:** Add an exception handler for `RequestValidationError` that returns a consistent JSON shape (e.g. `{ "detail": [...], "type": "validation_error" }`) so frontends can parse it uniformly.
- **Structured error codes:** For known cases (e.g. "no_llm_configured", "workspace_not_found"), return a stable `type` or `code` in the response so the UI can branch.
- **Never leak internals:** In production, avoid returning stack traces or raw exception messages in 500 responses; log them instead.

---

## 3. Health Checks

**Why:** Orchestrators (Kubernetes, ECS) and load balancers need to know if the app is ready and alive.

**Done / in place:**
- `GET /health` returns 200 with status/version/service (no dependencies).

**Recommendations:**
- **Readiness vs liveness:**  
  - **Liveness:** “Process is running.” Keep `GET /health` cheap (no DB).  
  - **Readiness:** “Ready to serve traffic.” Add e.g. `GET /health/ready` that pings the database (and optionally Redis). If DB is down, return 503 so the orchestrator doesn’t send traffic yet.
- **Startup:** In lifespan, optionally verify DB connectivity once at startup and fail fast (or log a warning) so misconfiguration is obvious.

---

## 4. Timeouts & Retries

**Why:** LLM and external services can hang; retries improve resilience for transient failures.

**Done / in place:**
- Agent: subprocess timeout for terminal commands; HTTP timeout for CodeLearn guidance.
- Celery tasks: retry with backoff in executor.
- Config: `AGENT_TIMEOUT_SECONDS`, `MAX_AGENT_RETRIES`.

**Recommendations:**
- **LLM calls:** Use a timeout on every call to OpenAI/Anthropic/local LLM (e.g. 60–120s). If the client supports it, set it in the LangChain wrapper or in `_generate()`.
- **Agent loop:** Consider an overall timeout for the whole `run_loop()` (e.g. 2–5 minutes) so a single request can’t hold a worker forever.
- **Retries:** For transient LLM/API errors (5xx, rate limits), retry with backoff in `_generate()` or in the service that calls the LLM; cap retries (e.g. 2–3) to avoid long waits.

---

## 5. Configuration & Environment

**Why:** Wrong config in production leads to security issues or silent failures.

**Done / in place:**
- Pydantic Settings with `.env` and defaults.
- Separate keys for OpenAI, Anthropic, local LLM.

**Recommendations:**
- **Production checks:** If `ENVIRONMENT=production`, warn or fail startup when `SECRET_KEY` is still the default or when critical API keys are missing (if the app requires them).
- **Secrets:** Never log API keys or tokens; redact in log formatters if needed.
- **CORS:** In production, set `CORS_ORIGINS` explicitly; avoid `["*"]` with credentials.

---

## 6. Database & Connections

**Why:** Connection leaks or pool exhaustion cause 500s under load.

**Done / in place:**
- SQLAlchemy with `pool_pre_ping=True`, `pool_size`, `max_overflow`.
- `get_db()` yields and closes the session in a `finally` block.

**Recommendations:**
- **Lifespan:** On startup, run a trivial query (e.g. `SELECT 1`) to verify DB connectivity; log or exit if it fails.
- **Read-only health:** Use a simple read for readiness (e.g. count a table or `SELECT 1`) so you don’t modify state.

---

## 7. Logging & Observability

**Why:** Good logs and metrics help diagnose production issues.

**Done / in place:**
- `logging_config.setup_logging()`; third-party loggers set to WARNING.
- Logger used in main and services.

**Recommendations:**
- **Structured logging:** In production, consider JSON logs (e.g. `structlog` or a custom formatter) so log aggregators can query by field.
- **Request ID:** Add middleware to assign a request ID and include it in logs and (optionally) in response headers.
- **Sensitive data:** Don’t log message content, tokens, or full request bodies; log request path, method, and maybe message count/length.

---

## 8. Security

**Why:** Reduce risk of abuse and data leaks.

**Done / in place:**
- JWT auth; `get_current_active_user` on protected routes.
- Path traversal blocked in agent kernel (`_safe_path`).
- Human-in-the-loop for edit_file and run_terminal.

**Recommendations:**
- **Rate limiting:** Config has `RATE_LIMIT_*`; implement middleware or a dependency that enforces per-user or per-IP limits on expensive endpoints (e.g. `/agent/chat`, `/build/generate`).
- **Workspace allowlist:** If the server runs in a shared environment, restrict `workspace_root` to a list of allowed directories.
- **Command allowlist/blocklist:** For `run_terminal`, consider blocking dangerous commands (e.g. `rm -rf /`, `curl | sh`) or allowing only a set of commands; document the policy.

---

## 9. Testing

**Why:** Tests catch regressions and document expected behavior.

**Done / in place:**
- Backend tests: agent kernel, builder service, semantic context, agent chat API (skipped when app/DB unavailable).
- Fixtures: `tmp_workspace`, `agent_context`.

**Recommendations:**
- **Run tests in CI** (e.g. GitHub Actions) on every PR.
- **Optional:** In-memory SQLite or test DB so agent chat API tests run without a real PostgreSQL.
- **Integration tests:** One or two tests that hit real endpoints (with mocked auth) to verify request/response shapes and error codes.

---

## 10. Quick Wins Checklist

| Area              | Action |
|-------------------|--------|
| Validation        | Add max length/count to agent chat messages and return 400 when exceeded. |
| Health            | Add `/health/ready` with DB ping; optional startup DB check in lifespan. |
| Errors            | Add `RequestValidationError` handler for consistent 422 JSON. |
| Config            | Warn on default `SECRET_KEY` when `ENVIRONMENT=production`. |
| Timeouts          | Ensure every LLM call has a timeout (config or code). |
| Logging           | Avoid logging full message content; log request path and status. |
| Rate limiting     | Implement rate limit middleware for `/agent/chat` and `/build/generate`. |

Implementing these in small steps will make the app more robust without a full rewrite.

---

## Implemented in This Repo

- **Validation:** Agent chat request schema enforces `max_length` on messages list (100) and per-message content (100KB); `min_length=1` on messages for `/chat`. Returns 422 when exceeded.
- **Request body size:** Middleware rejects bodies larger than `REQUEST_BODY_MAX_BYTES` (default 1MB) with 413 and `type: "payload_too_large"`.
- **Rate limiting:** Per-IP rate limit for `/api/v1/agent/chat`, `/api/v1/agent/execute-pending`, and `/api/v1/build/generate` (config: `RATE_LIMIT_AGENT_CHAT_PER_MINUTE`, `RATE_LIMIT_BUILD_GENERATE_PER_MINUTE`). Returns 429 and `type: "rate_limit_exceeded"`.
- **Request ID:** Middleware assigns `X-Request-ID` and sets `request_id_ctx`; response includes `X-Request-ID`; logging can include request_id (see logging_config).
- **Health:** `GET /health` (liveness, no deps); `GET /health/ready` (readiness, DB ping, returns 503 if DB unreachable).
- **Lifespan:** Startup runs a DB connectivity check (`SELECT 1`) and fails fast if DB is unreachable; warns when `ENVIRONMENT=production` and `SECRET_KEY` is still default; warns when CORS_ORIGINS includes `*` in production.
- **Errors:** `RequestValidationError` handler returns consistent JSON with `type: "validation_error"` and Pydantic `detail`. Agent errors return structured `type`: `no_llm_configured` (503), `workspace_not_allowed` (400), `agent_timeout` (408).
- **Logging:** `SecretsRedactionFilter` redacts secret-like substrings; `RequestIDFilter` adds request_id to log records; optional JSON formatter when `ENVIRONMENT=production`.
- **Config:** `LLM_REQUEST_TIMEOUT_SECONDS`, `WORKSPACE_ALLOWED_ROOTS` (optional allowlist), `REQUEST_BODY_MAX_BYTES`.
- **LLM:** Timeout on OpenAI/Anthropic clients; retries with backoff in `_generate()` (builder_service and agent kernel).
- **Agent kernel:** `run_loop()` has overall timeout (`AGENT_TIMEOUT_SECONDS`); workspace allowlist enforced when `WORKSPACE_ALLOWED_ROOTS` is set; command blocklist for `run_terminal` (e.g. `rm -rf /`, `| sh`, fork bomb patterns).
- **CI:** GitHub Actions workflow runs backend tests (excluding agent_chat_api when DB not available) on push/PR to main and develop.
