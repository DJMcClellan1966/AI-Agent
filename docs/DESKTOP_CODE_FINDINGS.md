# Desktop code review – ideas that could improve Synthesis

Searched `C:\Users\DJMcC\OneDrive\Desktop` for code that could benefit the app. Below: source, idea, and priority.

---

## 1. **CodeLearn – `llm_suggestions.py`** (cuddly-octo-computing-machine)

- **Pattern:** LLM chain: try OpenAI → then Ollama → then **template fallback** with a clear dict (e.g. `PATTERN_GUIDANCE`).
- **Use in Synthesis:** We already do template fallback in `builder_service` when the LLM fails. Could add a **small “app type / features” guidance dict** (keyword → type, keyword → feature) so the default spec is smarter when the LLM is missing or returns bad JSON.
- **Priority:** High (easy, improves offline/poor-LLM behavior).

---

## 2. **Special project – `ai-service.js`** (special_project)

- **Patterns:**
  - **Structured JSON prompt:** “Respond with JSON only” + exact schema in the prompt → fewer malformed answers.
  - **Extract JSON from response:** `content.match(/\{[\s\S]*\}/)` then `JSON.parse` when the model wraps JSON in markdown or extra text.
  - **Cloud vs local fallback:** Use cloud AI when available, else local (keyword/pattern) analysis.
  - **Confidence:** Return a confidence score; UI or backend can ask for clarification when low.
- **Use in Synthesis:**  
  - Make spec/code prompts even more explicit (e.g. “Reply with ONLY a JSON object…”).  
  - Use a single regex to pull the first `{ ... }` from the response before parsing (we already do similar; regex can be more robust).  
  - Optional: add a `confidence` or `needs_clarification` field to the spec and, if low, suggest follow-up questions.
- **Priority:** High for JSON extraction; medium for confidence/clarification.

---

## 3. **CodeLearn – `guidance_api.py`**

- **Pattern:** REST API with CORS, health check, and a **“suggest”** endpoint that takes context (e.g. pattern, file, code) and returns a suggestion (e.g. fix).
- **Use in Synthesis:**  
  - Add **`POST /api/v1/build/suggest-question`**: send current conversation; return 1–2 suggested follow-up questions (e.g. “Who will use this?” “Persistent data or session-only?”). Same LLM as now; improves the conversational feel before the user hits “Generate.”
- **Priority:** Medium (one new endpoint + one prompt).

---

## 4. **Original Synthesis – `synthesis/index.html`**

- **What’s there:** Scripted question bank, progress steps (“Understanding intent”, “Mapping structure”, “Synthesizing code”, “Final assembly”), architecture diagram (nodes), and “question options” (clickable chips for answers).
- **Use in Synthesis:**  
  - **Optional UI:** Add a “Suggested questions” area (from (3)) and/or progress steps that advance as the user sends messages and then hits Generate.  
  - Reuse the “question options” pattern as clickable suggestions for the next message (driven by suggest-question API).
- **Priority:** Low–medium (UI only, after (3) exists).

---

## 5. **Mycelium – `embeddings.py` / `api.py`** (mycelium)

- **Pattern:** Embed text with SentenceTransformers (`all-MiniLM-L6-v2`), store vectors, **semantic search** and “find similar” nodes.
- **Use in Synthesis:**  
  - **Later feature:** Store an embedding per project (e.g. from `conversation_summary` or spec). Then: “Find projects similar to this idea” or “Suggest features from past projects” using cosine similarity. Would need an embedding column (or separate table) and optional dependency on `sentence-transformers`.
- **Priority:** Low (nice-to-have, more effort).

---

## 6. **CodeLearn – guidance API (health, versioning)**

- **Pattern:** `/health`, optional `?minimal=1`, and `api_version` in responses.
- **Use in Synthesis:** We already have `/health`. Could add `api_version: "1"` to build responses and a `minimal` variant for list projects (e.g. id, name, created_at only) for lighter clients.
- **Priority:** Low.

---

## Summary

| Source            | Idea                              | Priority |
|-------------------|-----------------------------------|----------|
| llm_suggestions   | Keyword-based spec fallback        | High     |
| ai-service.js     | Robust JSON extraction + confidence| High     |
| guidance_api      | suggest-question endpoint         | Medium   |
| Synthesis HTML    | Progress steps, question chips    | Low–Med  |
| Mycelium          | Embeddings + similar projects     | Low      |

Implementing **robust JSON extraction** and **keyword-based spec fallback** in the builder service next.
