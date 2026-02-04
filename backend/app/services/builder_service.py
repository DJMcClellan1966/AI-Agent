"""
Builder service: conversation → spec → generated code (HTML/CSS/JS).
Uses the same LLM config as the rest of the app (OpenAI, Anthropic, or local).
"""
import json
import logging
import re
from typing import Dict, Any, List

from app.core.config import settings
from app.core.local_llm import get_local_llm

logger = logging.getLogger(__name__)

# Try LangChain imports (optional for local-only setups)
try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from langchain.chat_models import ChatOpenAI, ChatAnthropic
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False


def _get_llm():
    """Return LLM instance (LangChain or local)."""
    if settings.USE_LOCAL_LLM:
        local = get_local_llm()
        if local.is_available():
            return ("local", local)
        logger.warning("Local LLM not available, falling back to API")
    if not LANGCHAIN_AVAILABLE:
        return (None, None)
    if settings.OPENAI_API_KEY:
        return ("openai", ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.5,
            openai_api_key=settings.OPENAI_API_KEY,
        ))
    if settings.ANTHROPIC_API_KEY:
        return ("anthropic", ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            temperature=0.5,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
        ))
    return (None, None)


def _generate(llm_type: str, llm, prompt: str, max_tokens: int = 2000) -> str:
    """Generate text from prompt. llm_type is 'local', 'openai', or 'anthropic'."""
    if not llm:
        return ""
    try:
        if llm_type == "local":
            return llm.generate(prompt, max_tokens=max_tokens)
        # LangChain
        if hasattr(llm, "invoke"):
            return llm.invoke(prompt).content
        return llm.predict(prompt)
    except Exception as e:
        logger.error(f"LLM generate failed: {e}")
        return ""


def conversation_to_spec(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Turn conversation history into a structured project spec using the LLM.
    Returns dict with: name, type, features, persistence, theme, ui_complexity.
    """
    conv_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )
    prompt = f"""You are a product analyst. Based on this conversation about building a web app, extract a project spec.

Conversation:
{conv_text}

Reply with ONLY a JSON object (no markdown, no explanation) with exactly these keys:
- "name": short app name (e.g. "ReadingTracker")
- "type": one of "dashboard", "tracker", "notes", "todo", "library", "app"
- "features": list of feature keywords, e.g. ["tracking", "list management", "reminders", "search", "visualization", "theming", "export", "categorization", "streaks"]
- "persistence": "localStorage" or "session" or "none"
- "theme": "light" or "dark" or "system"
- "ui_complexity": "minimal" or "rich"

JSON:"""
    llm_type, llm = _get_llm()
    raw = _generate(llm_type, llm, prompt, max_tokens=600)
    if not raw:
        return _default_spec(messages)
    # Robust JSON extraction (handles markdown, trailing text, multiple braces)
    json_str = _extract_json_object(raw.strip())
    if not json_str:
        return _default_spec(messages)
    try:
        spec = json.loads(json_str)
        return {
            "name": spec.get("name", "MyApp"),
            "type": spec.get("type", "app"),
            "features": spec.get("features", []),
            "persistence": spec.get("persistence", "localStorage"),
            "theme": spec.get("theme", "dark"),
            "ui_complexity": spec.get("ui_complexity", "minimal"),
        }
    except json.JSONDecodeError:
        logger.warning("Could not parse spec JSON, using defaults")
        return _default_spec(messages)


def _extract_json_object(raw: str) -> str:
    """Extract first balanced {...} from text (robust to markdown or trailing text). O(n) single pass."""
    raw = raw.strip()
    start = raw.find("{")
    if start == -1:
        return ""
    depth = 0
    for i in range(start, len(raw)):
        if raw[i] == "{":
            depth += 1
        elif raw[i] == "}":
            depth -= 1
            if depth == 0:
                return raw[start : i + 1]
    # Fallback: first { to last }
    end = raw.rfind("}")
    if end != -1 and end > start:
        return raw[start : end + 1]
    return ""


def _default_spec(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Fallback spec when LLM is unavailable or parse fails. Uses keyword detection (from Synthesis + ai-service pattern)."""
    name = "MyApp"
    all_text = " ".join(m.get("content", "") for m in messages).lower()
    if messages:
        first = messages[0].get("content", "")[: 80]
        words = [w for w in first.split() if len(w) > 2][:2]
        if words:
            name = "".join(w.capitalize() for w in words)

    # Keyword -> app type (from Synthesis analyzeInput + special_project patterns)
    type_hints = [
        (["dashboard", "overview", "summary", "day at a glance"], "dashboard"),
        (["tracker", "tracking", "log", "habit", "streak"], "tracker"),
        (["note", "notes", "writing", "memo"], "notes"),
        (["todo", "task", "checklist", "to-do"], "todo"),
        (["reading", "book", "library"], "library"),
    ]
    app_type = "app"
    for keywords, t in type_hints:
        if any(k in all_text for k in keywords):
            app_type = t
            break

    # Feature keywords (from Synthesis featurePatterns)
    feature_keywords = [
        (["track", "tracking", "monitor"], "tracking"),
        (["list", "collection", "organize"], "list management"),
        (["remind", "notification", "alert"], "reminders"),
        (["search", "find", "filter"], "search"),
        (["chart", "graph", "visual", "stats"], "visualization"),
        (["dark", "theme", "light mode"], "theming"),
        (["export", "download", "backup"], "export"),
        (["tag", "category", "label"], "categorization"),
        (["streak", "habit", "daily"], "streaks"),
    ]
    features = []
    for keywords, feat in feature_keywords:
        if any(k in all_text for k in keywords) and feat not in features:
            features.append(feat)
    if not features:
        features = ["list management", "tracking"]

    # Theme
    theme = "dark"
    if "light mode" in all_text or "light theme" in all_text:
        theme = "light"
    elif "system" in all_text or "preference" in all_text:
        theme = "system"

    return {
        "name": name,
        "type": app_type,
        "features": features,
        "persistence": "localStorage",
        "theme": theme,
        "ui_complexity": "minimal",
    }


def spec_to_code(spec: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate HTML, CSS, and JS from a structured spec.
    Returns dict: { "index.html": "...", "styles.css": "...", "app.js": "..." }.
    """
    name = spec.get("name", "MyApp")
    app_type = spec.get("type", "app")
    features = spec.get("features", [])
    persistence = spec.get("persistence", "localStorage")
    theme = spec.get("theme", "dark")
    ui = spec.get("ui_complexity", "minimal")

    llm_type, llm = _get_llm()
    if not llm:
        return _template_code(name, app_type, features, persistence, theme, ui)

    # Single prompt for all three files to keep context
    prompt = f"""You are a front-end developer. Generate a complete, working single-page web app as three files.

Spec:
- App name: {name}
- App type: {app_type}
- Features: {", ".join(features)}
- Data: {persistence} (use localStorage if "localStorage", else in-memory)
- Theme: {theme}
- UI: {ui}

Rules:
- Plain HTML/CSS/JS only. No frameworks. No build step.
- index.html: one file, include <link rel="stylesheet" href="styles.css"> and <script src="app.js"></script>.
- styles.css: complete styles; use CSS variables for colors; support dark theme if theme is dark.
- app.js: implement the core feature (e.g. add/list/delete items for a tracker, with {persistence} if applicable). Use DOM APIs. No placeholder comments.

Reply in this exact format (no other text):
===INDEX.HTML===
<!DOCTYPE html>...
===STYLES.CSS===
...css...
===APP.JS===
...javascript...
===END==="""

    raw = _generate(llm_type, llm, prompt, max_tokens=4000)
    if not raw:
        return _template_code(name, app_type, features, persistence, theme, ui)

    files = _parse_code_blocks(raw)
    if not files:
        return _template_code(name, app_type, features, persistence, theme, ui)

    return files


def _parse_code_blocks(raw: str) -> Dict[str, str]:
    """Extract index.html, styles.css, app.js from ===FILENAME=== blocks."""
    files = {}
    pattern = r"===(INDEX\.HTML|STYLES\.CSS|APP\.JS)===\s*\n?(.*?)(?====|$)"
    for m in re.finditer(pattern, raw, re.DOTALL):
        label, content = m.group(1).strip(), m.group(2).strip()
        key = "index.html" if "INDEX" in label else "styles.css" if "STYLES" in label else "app.js"
        files[key] = content
    return files


def _template_code(
    name: str,
    app_type: str,
    features: List[str],
    persistence: str,
    theme: str,
    ui_complexity: str,
) -> Dict[str, str]:
    """Fallback: generate working code from templates when LLM is unavailable."""
    has_storage = persistence == "localStorage" or "tracking" in features or app_type == "tracker"
    has_viz = "visualization" in features

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="app">
        <header class="header">
            <h1>{name}</h1>
            <p class="tagline">Built through conversation</p>
        </header>
        <main class="main">
            <section class="input-section">
                <input type="text" id="newItem" placeholder="Add new entry...">
                <button onclick="addItem()">Add</button>
            </section>
            <section class="content-section">
                <div id="itemList" class="item-list"></div>
            </section>
            {"<section class='stats-section'><div class='stat-card'><span class='stat-value' id='totalCount'>0</span><span class='stat-label'>Total</span></div><div class='stat-card'><span class='stat-value' id='todayCount'>0</span><span class='stat-label'>Today</span></div></section>" if has_viz else ""}
        </main>
    </div>
    <script src="app.js"></script>
</body>
</html>"""

    css = """* { margin: 0; padding: 0; box-sizing: border-box; }
:root { --bg: #0f0f14; --surface: #1a1a22; --text: #e8e8ed; --text-dim: #888899; --accent: #6366f1; --success: #22c55e; }
body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
.app { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
.header { text-align: center; margin-bottom: 40px; }
.header h1 { font-size: 32px; font-weight: 600; margin-bottom: 8px; }
.tagline { color: var(--text-dim); font-size: 14px; }
.input-section { display: flex; gap: 12px; margin-bottom: 32px; }
.input-section input { flex: 1; padding: 14px 18px; background: var(--surface); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: var(--text); font-size: 15px; }
.input-section input:focus { outline: none; border-color: var(--accent); }
.input-section button { padding: 14px 24px; background: var(--accent); border: none; border-radius: 10px; color: white; font-weight: 600; cursor: pointer; }
.item-list { display: flex; flex-direction: column; gap: 12px; }
.item { padding: 16px 20px; background: var(--surface); border-radius: 12px; display: flex; align-items: center; justify-content: space-between; }
.item-text { font-size: 15px; }
.item-meta { font-size: 12px; color: var(--text-dim); }
.stats-section { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 32px; }
.stat-card { padding: 24px; background: var(--surface); border-radius: 12px; text-align: center; }
.stat-value { display: block; font-size: 36px; font-weight: 600; color: var(--accent); }
.stat-label { font-size: 13px; color: var(--text-dim); }"""

    key = f"{name.lower().replace(' ', '_')}_data"
    js = f"""// {name} - Generated by Synthesis
const APP_KEY = '{key}';
let items = [];
document.addEventListener('DOMContentLoaded', () => {{ loadData(); render(); }});
function loadData() {{ const s = localStorage.getItem(APP_KEY); if (s) items = JSON.parse(s); }}
function saveData() {{ localStorage.setItem(APP_KEY, JSON.stringify(items)); }}
function addItem() {{
  const input = document.getElementById('newItem');
  const text = input.value.trim();
  if (!text) return;
  items.unshift({{ id: Date.now(), text, createdAt: new Date().toISOString(), completed: false }});
  input.value = ''; saveData(); render();
}}
function toggleItem(id) {{ const i = items.find(x => x.id === id); if (i) {{ i.completed = !i.completed; saveData(); render(); }} }}
function deleteItem(id) {{ items = items.filter(x => x.id !== id); saveData(); render(); }}
function render() {{
  const list = document.getElementById('itemList');
  if (items.length === 0) {{ list.innerHTML = '<p style="text-align:center;color:var(--text-dim);padding:40px">No items yet.</p>'; return; }}
  list.innerHTML = items.map(i => `<div class="item"> <div> <div class="item-text">${{escapeHtml(i.text)}}</div> <div class="item-meta">${{new Date(i.createdAt).toLocaleString()}}</div> </div> <button onclick="deleteItem(${{i.id}})" style="background:none;border:none;color:var(--text-dim);cursor:pointer">×</button> </div>`).join('');
  const tc = document.getElementById('totalCount'); const td = document.getElementById('todayCount');
  if (tc) tc.textContent = items.length;
  if (td) td.textContent = items.filter(i => new Date(i.createdAt).toDateString() === new Date().toDateString()).length;
}}
function escapeHtml(t) {{ const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }}
document.addEventListener('keydown', e => {{ if (e.key === 'Enter' && document.activeElement.id === 'newItem') addItem(); }});"""

    return {"index.html": html, "styles.css": css, "app.js": js}


def build_conversation_summary(messages: List[Dict[str, str]], max_len: int = 500) -> str:
    """Short summary of the conversation for storage."""
    if not messages:
        return ""
    parts = [m["content"][:200] for m in messages[:5]]
    summary = " | ".join(parts)
    return summary[:max_len] if len(summary) > max_len else summary


# Template follow-up questions when LLM is unavailable (from Synthesis question bank)
_SUGGEST_QUESTION_TEMPLATES = [
    (
        ["dashboard", "tracker", "notes", "todo", "habit", "reading", "list"],
        [
            "What's the core problem this solves for you?",
            "Who will use this—just you or others too?",
            "Should it remember things between sessions (persistent) or session-only?",
        ],
    ),
    (
        [],  # default
        [
            "What's the one thing it must do well?",
            "Minimal and focused UI, or rich with more features?",
            "Light mode, dark mode, or follow system preference?",
        ],
    ),
]


def suggest_questions(messages: List[Dict[str, str]], max_questions: int = 2) -> List[str]:
    """
    Suggest 1–2 follow-up questions to clarify the app idea (CodeLearn-style suggest endpoint).
    Uses LLM when available; otherwise template based on conversation keywords.
    """
    if not messages:
        return [
            "What's the core problem this app solves for you?",
            "Who will use it—just you or others too?",
        ][:max_questions]

    conv_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
    all_text = " ".join(m["content"] for m in messages).lower()

    llm_type, llm = _get_llm()
    if llm:
        prompt = f"""You are a product analyst helping someone describe a web app idea. Based on this short conversation, suggest exactly {max_questions} short follow-up questions to clarify what they want. Questions should be practical (e.g. who will use it, persistence, must-have feature). Reply with ONLY a JSON array of strings, e.g. ["Question one?", "Question two?"]. No other text.

Conversation:
{conv_text}

JSON array of {max_questions} questions:"""
        raw = _generate(llm_type, llm, prompt, max_tokens=200)
        if raw:
            json_str = _extract_json_array(raw)
            if json_str:
                try:
                    arr = json.loads(json_str)
                    if isinstance(arr, list):
                        return [str(q) for q in arr[:max_questions] if q]
                except json.JSONDecodeError:
                    pass

    # Template fallback: pick questions based on keywords
    for keywords, questions in _SUGGEST_QUESTION_TEMPLATES:
        if not keywords or any(k in all_text for k in keywords):
            return questions[:max_questions]
    return _SUGGEST_QUESTION_TEMPLATES[-1][1][:max_questions]


def _extract_json_array(raw: str) -> str:
    """Extract first balanced [...] from text."""
    raw = raw.strip()
    start = raw.find("[")
    if start == -1:
        return ""
    depth = 0
    for i in range(start, len(raw)):
        if raw[i] == "[":
            depth += 1
        elif raw[i] == "]":
            depth -= 1
            if depth == 0:
                return raw[start : i + 1]
    end = raw.rfind("]")
    if end != -1 and end > start:
        return raw[start : end + 1]
    return ""
