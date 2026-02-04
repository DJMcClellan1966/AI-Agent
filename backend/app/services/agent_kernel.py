"""
Agent kernel: LLM + tool loop. Starting point for "your own agent like Cursor."
Run a conversation; LLM can call tools; edit_file and run_terminal require human approval.
"""
import json
import logging
import os
import difflib
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from app.services.builder_service import (
    _get_llm,
    _generate,
    suggest_questions,
    conversation_to_spec,
    spec_to_code,
    build_conversation_summary,
    _extract_json_object,
)

logger = logging.getLogger(__name__)

# When a tool returns this key, the loop returns pending_approval instead of executing
PENDING_APPROVAL_KEY = "__pending_approval__"

# Tool: name, description, function(context, **args) -> str or pending_approval dict
ToolSpec = Dict[str, Any]


def _tool_suggest_questions(context: Dict[str, Any], messages: List[Dict[str, str]]) -> str:
    qs = suggest_questions(messages, max_questions=2)
    return json.dumps({"questions": qs})


def _tool_generate_app(context: Dict[str, Any], messages: List[Dict[str, str]]) -> str:
    spec = conversation_to_spec(messages)
    files = spec_to_code(spec)
    summary = build_conversation_summary(messages)
    return json.dumps({
        "spec": spec,
        "files": list(files.keys()),
        "summary": summary,
        "message": f"Generated app '{spec.get('name', 'MyApp')}' with {len(files)} files.",
    })


def _safe_path(root: str, path: str) -> Optional[str]:
    """Resolve path under workspace_root; return None if outside. O(1) path ops."""
    if not root:
        return None
    full = os.path.normpath(os.path.join(root, path.lstrip("/")))
    if not full.startswith(os.path.abspath(root)):
        return None
    return full


def _tool_read_file(context: Dict[str, Any], path: str) -> str:
    root = context.get("workspace_root") or ""
    if not root:
        return json.dumps({"error": "Workspace not configured. Set workspace_root in context."})
    full = _safe_path(root, path)
    if not full:
        return json.dumps({"error": "Path outside workspace."})
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            return json.dumps({"path": path, "content": f.read()})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_list_dir(context: Dict[str, Any], path: str = ".") -> str:
    root = context.get("workspace_root") or ""
    if not root:
        return json.dumps({"error": "Workspace not configured. Set workspace_root in context."})
    full = _safe_path(root, path)
    if not full:
        return json.dumps({"error": "Path outside workspace."})
    try:
        entries = os.listdir(full)
        return json.dumps({"path": path, "entries": entries})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_search_files(context: Dict[str, Any], pattern: str, path: str = ".") -> str:
    """Search for pattern in workspace files (literal substring). Returns path, line_no, line."""
    root = context.get("workspace_root") or ""
    if not root:
        return json.dumps({"error": "Workspace not configured. Set workspace_root in context."})
    base_full = _safe_path(root, path)
    if not base_full:
        return json.dumps({"error": "Path outside workspace."})
    if not pattern:
        return json.dumps({"error": "pattern is required."})
    # Text extensions to search; skip binary and large dirs
    text_ext = (".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".md", ".txt", ".yml", ".yaml", ".toml", ".sh", ".bat", ".env")
    max_matches = 100
    max_file_size = 500_000
    matches: List[Dict[str, Any]] = []
    try:
        for dirpath, _dirnames, filenames in os.walk(base_full):
            if len(matches) >= max_matches:
                break
            rel_dir = os.path.relpath(dirpath, base_full) if dirpath != base_full else "."
            for name in filenames:
                if len(matches) >= max_matches:
                    break
                if not (name.endswith(text_ext) or "." not in name):
                    continue
                full_path = os.path.join(dirpath, name)
                try:
                    size = os.path.getsize(full_path)
                    if size > max_file_size:
                        continue
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        for line_no, line in enumerate(f, 1):
                            if pattern in line:
                                rel_path = os.path.join(rel_dir, name) if rel_dir != "." else name
                                matches.append({"path": rel_path.replace("\\", "/"), "line": line_no, "content": line.rstrip()[:200]})
                                if len(matches) >= max_matches:
                                    break
                except (OSError, UnicodeDecodeError):
                    continue
        return json.dumps({"pattern": pattern, "path": path, "matches": matches})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_edit_file_preview(context: Dict[str, Any], path: str, old_string: str, new_string: str) -> Dict[str, Any]:
    """Return pending_approval with diff preview; does not write."""
    root = context.get("workspace_root") or ""
    if not root:
        return {PENDING_APPROVAL_KEY: True, "tool": "edit_file", "args": {"path": path, "old_string": old_string, "new_string": new_string}, "preview": "Workspace not configured.", "error": True}
    full = _safe_path(root, path)
    if not full:
        return {PENDING_APPROVAL_KEY: True, "tool": "edit_file", "args": {"path": path, "old_string": old_string, "new_string": new_string}, "preview": "Path outside workspace.", "error": True}
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            current = f.read()
    except Exception as e:
        return {PENDING_APPROVAL_KEY: True, "tool": "edit_file", "args": {"path": path, "old_string": old_string, "new_string": new_string}, "preview": f"Cannot read file: {e}", "error": True}
    if old_string not in current:
        return {PENDING_APPROVAL_KEY: True, "tool": "edit_file", "args": {"path": path, "old_string": old_string, "new_string": new_string}, "preview": "old_string not found in file (file may have changed).", "error": True}
    new_content = current.replace(old_string, new_string, 1)
    diff = "\n".join(difflib.unified_diff(current.splitlines(), new_content.splitlines(), lineterm="", fromfile=path, tofile=path))
    preview = diff[:4000] + ("..." if len(diff) > 4000 else "")
    return {PENDING_APPROVAL_KEY: True, "tool": "edit_file", "args": {"path": path, "old_string": old_string, "new_string": new_string}, "preview": preview}


def _execute_edit_file(context: Dict[str, Any], path: str, old_string: str, new_string: str) -> str:
    """Actually perform the edit. Call after user approval."""
    full = _safe_path(context.get("workspace_root") or "", path)
    if not full:
        return json.dumps({"error": "Path outside workspace or workspace not set."})
    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if old_string not in content:
            return json.dumps({"error": "old_string not found in file."})
        new_content = content.replace(old_string, new_string, 1)
        with open(full, "w", encoding="utf-8") as f:
            f.write(new_content)
        return json.dumps({"path": path, "status": "updated"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_run_terminal_preview(context: Dict[str, Any], command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Return pending_approval with command preview; does not run."""
    preview = f"Command: {command}"
    if cwd:
        preview += f"\nCwd: {cwd}"
    return {PENDING_APPROVAL_KEY: True, "tool": "run_terminal", "args": {"command": command, "cwd": cwd}, "preview": preview}


def _execute_run_terminal(context: Dict[str, Any], command: str, cwd: Optional[str] = None) -> str:
    """Actually run the command. Call after user approval."""
    root = context.get("workspace_root") or ""
    run_cwd = root
    if cwd:
        run_cwd = _safe_path(root, cwd) or root
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=run_cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return json.dumps({
            "stdout": result.stdout[:8000],
            "stderr": result.stderr[:2000],
            "returncode": result.returncode,
        })
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Command timed out after 60s."})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_default_tools(context: Optional[Dict[str, Any]] = None) -> List[ToolSpec]:
    """Tools available to the agent. Context can override codeiq_enabled / codeiq_workspace (from UI toggles)."""
    context = context or {}

    def _suggest(ctx: Dict[str, Any], **kwargs: Any) -> str:
        msgs = kwargs.get("messages") or []
        return _tool_suggest_questions(ctx, msgs)

    def _generate_app(ctx: Dict[str, Any], **kwargs: Any) -> str:
        msgs = kwargs.get("messages") or []
        return _tool_generate_app(ctx, msgs)

    return [
        {
            "name": "suggest_questions",
            "description": "Suggest 1-2 short follow-up questions to clarify the user's app or task. Input: messages (list of {role, content}).",
            "function": _suggest,
        },
        {
            "name": "generate_app",
            "description": "Generate a web app (HTML/CSS/JS) from the conversation so far. Input: messages (list of {role, content}). Use when the user is done describing and wants the app.",
            "function": _generate_app,
        },
        {
            "name": "read_file",
            "description": "Read a file from the workspace. Input: path (relative path). Requires workspace_root in context.",
            "function": _tool_read_file,
        },
        {
            "name": "list_dir",
            "description": "List directory contents in the workspace. Input: path (relative path, default '.'). Requires workspace_root in context.",
            "function": _tool_list_dir,
        },
        {
            "name": "search_files",
            "description": "Search for a literal string in workspace files (e.g. 'TODO', 'def foo'). Input: pattern or query (required), path (optional, default '.'). Returns matching path, line number, and line content. Requires workspace_root in context.",
            "function": lambda ctx, pattern=None, path=".", **kwargs: _tool_search_files(ctx, pattern or kwargs.get("query") or "", path or kwargs.get("path") or "."),
        },
        {
            "name": "edit_file",
            "description": "Edit a file: replace old_string with new_string (first occurrence). Requires user approval. Input: path, old_string, new_string. Requires workspace_root in context.",
            "function": lambda ctx, path=None, old_string=None, new_string=None: _tool_edit_file_preview(ctx, path or "", old_string or "", new_string or ""),
        },
        {
            "name": "run_terminal",
            "description": "Run a shell command in the workspace. Requires user approval. Input: command (str), cwd (optional, relative path). Requires workspace_root in context.",
            "function": lambda ctx, command=None, cwd=None: _tool_run_terminal_preview(ctx, command or "", cwd),
        },
        *_get_codeiq_tools(context),
    ]


def _get_workspace_context_block(context: Dict[str, Any], messages: List[Dict[str, str]]) -> str:
    """Build a short workspace context for the system prompt (Path 2 light: no embeddings)."""
    root = (context.get("workspace_root") or "").strip()
    if not root or not os.path.isdir(root):
        return ""
    lines = ["\nWorkspace context (workspace_root is set):"]
    try:
        entries = os.listdir(root)
        # Top-level only, cap at 40 items
        top = sorted(entries)[:40]
        lines.append("Top-level files/dirs: " + ", ".join(top))
    except OSError:
        lines.append("(could not list workspace)")
    # Optional: quick search using last user message keywords (no embeddings)
    last_user = None
    for m in reversed(messages):
        if m.get("role") == "user" and (m.get("content") or "").strip():
            last_user = (m.get("content") or "").strip()
            break
    if last_user and context.get("inject_search_context") is not False:
        words = [w for w in last_user.replace(",", " ").split() if len(w) > 3][:5]
        if words:
            for w in words[:2]:  # at most 2 quick searches
                try:
                    raw = _tool_search_files(context, w, ".")
                    data = json.loads(raw)
                    if data.get("matches"):
                        for hit in data["matches"][:5]:
                            lines.append(f"  {hit.get('path', '')}:{hit.get('line', '')} {hit.get('content', '')[:80]}")
                        break  # one search is enough for context
                except (json.JSONDecodeError, TypeError):
                    pass
    return "\n".join(lines) if len(lines) > 1 else ""


def run_loop(
    messages: List[Dict[str, str]],
    context: Optional[Dict[str, Any]] = None,
    tools: Optional[List[ToolSpec]] = None,
    max_turns: int = 5,
) -> Tuple[List[Dict[str, str]], Optional[str], Optional[Dict[str, Any]]]:
    """
    Run the agent loop: LLM can call tools or return a final reply.
    Returns (updated_messages, final_reply_text, pending_approval).
    When a tool returns pending_approval (edit_file, run_terminal), reply is None and pending_approval is set.
    Unless context.autonomous is True, in which case the tool is executed and the loop continues.
    Time: O(max_turns * (|messages| + LLM call)); tool_map build O(|tools|).
    """
    context = context or {}
    tools = tools or get_default_tools(context)
    tool_map = {t["name"]: t for t in tools}

    # Optional: inject CodeLearn guidance (cuddly-octo); context can override url and enabled
    guidance_block = _get_codelearn_guidance_block(context)
    workspace_block = _get_workspace_context_block(context, messages)
    tool_descriptions = "\n".join(
        f"- {t['name']}: {t['description']}" for t in tools
    )

    approval_note = " For file edits or running commands, use edit_file or run_terminal; the user will approve before they run."
    if context.get("autonomous"):
        approval_note = " Autonomous mode: edit_file and run_terminal will run immediately without asking."

    system = f"""You are a helpful coding and product assistant. You have access to these tools:

{tool_descriptions}
{guidance_block}{workspace_block}

Reply with JSON only. Either:
1) To call a tool: {{"thought": "brief reasoning", "tool": "tool_name", "args": {{...}}}}
   Use "messages" for the current conversation when a tool needs it (list of {{"role": "user"|"system", "content": "..."}}).
2) To reply to the user and finish: {{"thought": "brief reasoning", "reply": "your reply text"}}

Be concise.{approval_note}"""

    current = list(messages)
    # Avoid duplicating system prompt when continuing a conversation (e.g. after execute_pending)
    if not current or current[0].get("role") != "system" or "You are a helpful coding" not in (current[0].get("content") or ""):
        current.insert(0, {"role": "system", "content": system})

    llm_type, llm = _get_llm()
    if not llm:
        return current, "I don't have an LLM configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.", None

    for turn in range(max_turns):
        conv_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in current
        )
        prompt = f"""Current conversation:

{conv_text}

Your next step (JSON only):"""

        raw = _generate(llm_type, llm, prompt, max_tokens=600)
        if not raw:
            return current, "I couldn't generate a response. Check your LLM configuration.", None

        json_str = _extract_json_object(raw.strip())
        if not json_str:
            if "reply" not in raw.lower() and "tool" not in raw.lower():
                return current, raw[:1000], None
            return current, "I didn't understand the response format.", None

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return current, "I couldn't parse my own response. Please try again.", None

        if data.get("reply"):
            return current, (data.get("reply") or "").strip(), None

        tool_name = data.get("tool")
        args = data.get("args") or {}
        if not tool_name or tool_name not in tool_map:
            current.append({
                "role": "system",
                "content": f"[Invalid tool: {tool_name}. Valid: {list(tool_map.keys())}]",
            })
            continue

        if tool_name in ("suggest_questions", "generate_app") and "messages" not in args:
            args["messages"] = [{"role": m["role"], "content": m["content"]} for m in current]

        fn = tool_map[tool_name]["function"]
        try:
            result = fn(context, **args)
        except Exception as e:
            result = json.dumps({"error": str(e)})
            logger.exception("Tool %s failed", tool_name)

        # Human-in-the-loop: tool returned pending approval (unless autonomous)
        if isinstance(result, dict) and result.get(PENDING_APPROVAL_KEY):
            if context.get("autonomous") and tool_name in ("edit_file", "run_terminal"):
                # Execute immediately and continue the loop
                args = result.get("args") or {}
                if tool_name == "edit_file":
                    result = _execute_edit_file(
                        context,
                        args.get("path", ""),
                        args.get("old_string", ""),
                        args.get("new_string", ""),
                    )
                else:
                    result = _execute_run_terminal(
                        context,
                        args.get("command", ""),
                        args.get("cwd"),
                    )
            else:
                return current, None, result

        current.append({
            "role": "system",
            "content": f"[Tool {tool_name} result]: {result}",
        })

    return current, "I hit the turn limit. Please try a shorter conversation or rephrase.", None


def execute_pending_and_continue(
    messages: List[Dict[str, str]],
    context: Dict[str, Any],
    approved_tool: str,
    approved_args: Dict[str, Any],
    max_turns_after: int = 3,
) -> Tuple[List[Dict[str, str]], Optional[str], Optional[Dict[str, Any]]]:
    """
    Execute an approved edit_file or run_terminal, append result to messages, run the loop again.
    Returns (updated_messages, reply, pending_approval).
    """
    root = context.get("workspace_root") or ""
    result_str: str
    if approved_tool == "edit_file":
        result_str = _execute_edit_file(
            context,
            approved_args.get("path", ""),
            approved_args.get("old_string", ""),
            approved_args.get("new_string", ""),
        )
    elif approved_tool == "run_terminal":
        result_str = _execute_run_terminal(
            context,
            approved_args.get("command", ""),
            approved_args.get("cwd"),
        )
    else:
        result_str = json.dumps({"error": f"Unknown tool: {approved_tool}"})

    # Build state: use messages that the frontend sent (full history including system/tool turns)
    current = list(messages)
    current.append({
        "role": "system",
        "content": f"[User approved {approved_tool}. Result]: {result_str}",
    })

    return run_loop(
        messages=current,
        context=context,
        max_turns=max_turns_after,
    )


def _get_codeiq_tools(context: Optional[Dict[str, Any]] = None) -> List[ToolSpec]:
    """Optional CodeIQ tools (cuddly-octo). Context can set codeiq_enabled=False or codeiq_workspace (overrides env)."""
    context = context or {}
    if context.get("codeiq_enabled") is False:
        return []
    workspace = (context.get("codeiq_workspace") or os.environ.get("CODEIQ_WORKSPACE") or "").strip()
    if not workspace or not os.path.isdir(workspace):
        return []

    def _run_codeiq(subcmd: str, *args: str) -> str:
        try:
            cmd = [subprocess.get_executable(), "-m", "codeiq.cli", subcmd] + list(args)
            r = subprocess.run(cmd, cwd=workspace, capture_output=True, text=True, timeout=30)
            out = (r.stdout or "") + (r.stderr or "")
            return out[:6000] if out else "No output."
        except Exception as e:
            return f"CodeIQ error: {e}"

    def _search(ctx: Dict[str, Any], query: Optional[str] = None, **kwargs: Any) -> str:
        q = query or kwargs.get("query") or ""
        if not q:
            return json.dumps({"error": "query required"})
        return json.dumps({"query": q, "output": _run_codeiq("search", q)})

    def _analyze(ctx: Dict[str, Any], path: Optional[str] = None, **kwargs: Any) -> str:
        p = path or kwargs.get("path") or "."
        return json.dumps({"path": p, "output": _run_codeiq("analyze")})

    return [
        {
            "name": "search_code",
            "description": "Semantic search over the codebase (CodeIQ). Input: query (string). Set CODEIQ_WORKSPACE to enable.",
            "function": _search,
        },
        {
            "name": "analyze_code",
            "description": "Run code analysis (issues, duplicates, complexity) on the workspace (CodeIQ). Input: path (optional). Set CODEIQ_WORKSPACE to enable.",
            "function": _analyze,
        },
    ]


def _get_codelearn_guidance_block(context: Optional[Dict[str, Any]] = None) -> str:
    """If CodeLearn URL is set (context or env), fetch avoid/encourage. Context can set codelearn_enabled=False or codelearn_guidance_url."""
    context = context or {}
    if context.get("codelearn_enabled") is False:
        return ""
    url = (context.get("codelearn_guidance_url") or os.environ.get("CODELEARN_GUIDANCE_URL") or "").strip()
    if not url:
        return ""
    try:
        import urllib.request
        req = urllib.request.Request(url.rstrip("/") + "/guidance", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        avoid = data.get("avoid", [])[:5]
        encourage = data.get("encourage", [])[:5]
        if not avoid and not encourage:
            return ""
        lines = ["\nCode quality guidance (from CodeLearn):"]
        if avoid:
            lines.append("Avoid: " + "; ".join(a.get("pattern", a) if isinstance(a, dict) else str(a) for a in avoid))
        if encourage:
            lines.append("Encourage: " + "; ".join(e.get("pattern", e) if isinstance(e, dict) else str(e) for e in encourage))
        return "\n".join(lines)
    except Exception as e:
        logger.debug("CodeLearn guidance fetch failed: %s", e)
        return ""
