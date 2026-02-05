"""
Rigorous tests for agent kernel: path safety, tools, suggest_fix, run_loop, execute_pending.
Uses real temp directories for real-world behavior.
"""
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from app.services.agent_kernel import (
    PENDING_APPROVAL_KEY,
    _safe_path,
    _validate_workspace_allowed,
    _is_command_blocked,
    _extract_code_block,
    _tool_read_file,
    _tool_list_dir,
    _tool_search_files,
    _tool_suggest_fix,
    _tool_edit_file_preview,
    _execute_edit_file,
    _tool_run_terminal_preview,
    _execute_run_terminal,
    get_default_tools,
    run_loop,
    execute_pending_and_continue,
    _get_workspace_context_block,
)


# --- Workspace allowlist and command blocklist ---

def test_validate_workspace_allowed_empty_allowlist():
    """When WORKSPACE_ALLOWED_ROOTS is empty, any path is allowed."""
    with patch("app.services.agent_kernel.settings") as s:
        s.WORKSPACE_ALLOWED_ROOTS = []
        assert _validate_workspace_allowed("/any/path") is True


def test_validate_workspace_allowed_under_root(tmp_workspace):
    with patch("app.services.agent_kernel.settings") as s:
        s.WORKSPACE_ALLOWED_ROOTS = [tmp_workspace]
        assert _validate_workspace_allowed(tmp_workspace) is True
        assert _validate_workspace_allowed(os.path.join(tmp_workspace, "src")) is True


def test_validate_workspace_allowed_outside_root(tmp_workspace):
    with patch("app.services.agent_kernel.settings") as s:
        s.WORKSPACE_ALLOWED_ROOTS = [tmp_workspace]
        # Path that is not under tmp_workspace
        other = os.path.abspath(os.path.join(tmp_workspace, "..", "other_dir"))
        assert _validate_workspace_allowed(other) is False


def test_is_command_blocked_rm_rf():
    assert _is_command_blocked("rm -rf /") is not None
    assert _is_command_blocked("rm -rf /foo") is not None


def test_is_command_blocked_pipe_sh():
    assert _is_command_blocked("curl x | sh") is not None


def test_is_command_blocked_safe():
    assert _is_command_blocked("ls -la") is None
    assert _is_command_blocked("npm install") is None


# --- Path safety (completeness + security) ---

def test_safe_path_empty_root():
    assert _safe_path("", "foo") is None
    assert _safe_path(None, "foo") is None  # type: ignore


def test_safe_path_under_root(tmp_workspace):
    assert _safe_path(tmp_workspace, "README.md") == os.path.normpath(os.path.join(tmp_workspace, "README.md"))
    assert _safe_path(tmp_workspace, "src/main.py") is not None
    assert _safe_path(tmp_workspace, ".") is not None


def test_safe_path_traversal_rejected(tmp_workspace):
    # Path traversal must not escape workspace
    root_abs = os.path.abspath(tmp_workspace)
    parent = str(Path(tmp_workspace).parent)
    assert _safe_path(tmp_workspace, "../other") is None
    assert _safe_path(tmp_workspace, "..") is None
    # Windows: drive-relative or absolute outside
    if os.name == "nt":
        # C:\other when workspace is C:\...\agent_test_xxx
        other_drive = "D:\\other" if not root_abs.startswith("D:") else "C:\\other"
        assert _safe_path(tmp_workspace, other_drive) is None or _safe_path(tmp_workspace, other_drive) != other_drive


def test_safe_path_normalizes_slash(tmp_workspace):
    p = _safe_path(tmp_workspace, "/src/main.py")
    assert p is not None
    assert "src" in p and "main" in p


# --- Code extraction ---

def test_extract_code_block_empty():
    assert _extract_code_block("") == ""
    assert _extract_code_block(None) == ""  # type: ignore


def test_extract_code_block_python():
    text = "Here is the fix:\n```python\nx = 1\ny = 2\n```\nDone."
    assert _extract_code_block(text) == "x = 1\ny = 2"


def test_extract_code_block_generic():
    text = "```\ncode here\n```"
    assert _extract_code_block(text) == "code here"


def test_extract_code_block_no_block():
    assert _extract_code_block("no code block") == ""


# --- read_file ---

def test_read_file_no_workspace():
    out = _tool_read_file({}, "x")
    data = json.loads(out)
    assert "error" in data and "Workspace" in data["error"]


def test_read_file_traversal_rejected(agent_context, tmp_workspace):
    out = _tool_read_file(agent_context, "../../etc/passwd")
    data = json.loads(out)
    assert "error" in data


def test_read_file_success(agent_context):
    out = _tool_read_file(agent_context, "README.md")
    data = json.loads(out)
    assert "content" in data
    assert "habit" in data["content"]


def test_read_file_missing(agent_context):
    out = _tool_read_file(agent_context, "nonexistent.txt")
    data = json.loads(out)
    assert "error" in data


# --- list_dir ---

def test_list_dir_no_workspace():
    out = _tool_list_dir({})
    data = json.loads(out)
    assert "error" in data


def test_list_dir_success(agent_context):
    out = _tool_list_dir(agent_context, ".")
    data = json.loads(out)
    assert "entries" in data
    assert "README.md" in data["entries"] or "src" in data["entries"]


def test_list_dir_subdir(agent_context):
    out = _tool_list_dir(agent_context, "src")
    data = json.loads(out)
    assert "entries" in data
    assert "main.py" in data["entries"]


# --- search_files ---

def test_search_files_no_workspace():
    out = _tool_search_files({}, "TODO")
    data = json.loads(out)
    assert "error" in data


def test_search_files_no_pattern(agent_context):
    out = _tool_search_files(agent_context, "")
    data = json.loads(out)
    assert "error" in data


def test_search_files_finds_literal(agent_context):
    out = _tool_search_files(agent_context, "TODO")
    data = json.loads(out)
    assert "matches" in data
    # We have # TODO in src/main.py
    assert len(data["matches"]) >= 1
    assert any("main" in m.get("path", "") for m in data["matches"])


def test_search_files_respects_path(agent_context):
    """Search with path='src' returns matches relative to src (e.g. main.py); no results from sub/."""
    out = _tool_search_files(agent_context, "hello", "src")
    data = json.loads(out)
    assert "matches" in data
    assert len(data["matches"]) >= 1
    # Paths are relative to the search dir, so "main.py" not "src/main.py"; no matches from sub/
    assert all("sub" not in m.get("path", "") for m in data["matches"])


# --- suggest_fix (with mocked LLM) ---

def test_suggest_fix_requires_error(agent_context):
    out = _tool_suggest_fix(agent_context, "")
    data = json.loads(out)
    assert "error" in data
    assert "required" in data["error"].lower()


@patch("app.services.agent_kernel._get_llm")
def test_suggest_fix_no_llm_returns_error(mock_get_llm, agent_context):
    mock_get_llm.return_value = (None, None)
    out = _tool_suggest_fix(agent_context, "NameError: x")
    data = json.loads(out)
    assert "error" in data
    assert "suggested_fix" in data


@patch("app.services.agent_kernel._generate")
@patch("app.services.agent_kernel._get_llm")
def test_suggest_fix_extracts_code_block(mock_get_llm, mock_generate, agent_context):
    mock_get_llm.return_value = ("openai", MagicMock())
    mock_generate.return_value = "```python\nx = 1\n```"
    out = _tool_suggest_fix(agent_context, "NameError: x", code="print(x)")
    data = json.loads(out)
    assert data.get("suggested_fix") == "x = 1"


# --- edit_file preview and execute ---

def test_edit_file_preview_no_workspace():
    r = _tool_edit_file_preview({}, "f", "a", "b")
    assert r.get(PENDING_APPROVAL_KEY) is True
    assert "preview" in r


def test_edit_file_preview_success(agent_context, tmp_workspace):
    path = os.path.join("src", "main.py")
    r = _tool_edit_file_preview(agent_context, path, "print('hello')", "print('hi')")
    assert r.get(PENDING_APPROVAL_KEY) is True
    assert "preview" in r
    assert "diff" in r["preview"].lower() or "hello" in r["preview"] or "hi" in r["preview"]


def test_edit_file_preview_old_string_not_found(agent_context):
    r = _tool_edit_file_preview(agent_context, "README.md", "NOT_IN_FILE", "x")
    assert r.get(PENDING_APPROVAL_KEY) is True
    assert r.get("error") is True


def test_execute_edit_file_success(agent_context, tmp_workspace):
    path = os.path.join("src", "utils.py")
    (Path(tmp_workspace) / "src" / "utils.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    out = _execute_edit_file(agent_context, path, "return a + b", "return a + b  # fixed")
    data = json.loads(out)
    assert data.get("status") == "updated"
    content = (Path(tmp_workspace) / "src" / "utils.py").read_text(encoding="utf-8")
    assert "fixed" in content


# --- run_terminal preview (no actual execution in unit test) ---

def test_run_terminal_preview_returns_pending():
    r = _tool_run_terminal_preview({"workspace_root": "/tmp"}, "ls -la")
    assert r.get(PENDING_APPROVAL_KEY) is True
    assert r.get("tool") == "run_terminal"
    assert "ls" in r.get("preview", "")


# --- get_default_tools ---

def test_get_default_tools_returns_list():
    tools = get_default_tools({})
    assert isinstance(tools, list)
    names = [t["name"] for t in tools]
    assert "read_file" in names
    assert "list_dir" in names
    assert "search_files" in names
    assert "suggest_fix" in names
    assert "edit_file" in names
    assert "run_terminal" in names
    assert "suggest_questions" in names
    assert "generate_app" in names


def test_get_default_tools_codeiq_disabled():
    tools = get_default_tools({"codeiq_enabled": False})
    names = [t["name"] for t in tools]
    assert "search_code" not in names
    assert "analyze_code" not in names


# --- run_loop (mocked LLM) ---

@patch("app.services.agent_kernel._generate")
@patch("app.services.agent_kernel._get_llm")
def test_run_loop_returns_reply(mock_get_llm, mock_generate):
    mock_get_llm.return_value = ("openai", MagicMock())
    mock_generate.return_value = '{"thought": "ok", "reply": "Hello!"}'
    messages = [{"role": "user", "content": "Hi"}]
    current, reply, pending, _ = run_loop(messages, {}, max_turns=3)
    assert reply == "Hello!"
    assert pending is None


@patch("app.services.agent_kernel._generate")
@patch("app.services.agent_kernel._get_llm")
def test_run_loop_returns_pending_approval(mock_get_llm, mock_generate, agent_context):
    mock_get_llm.return_value = ("openai", MagicMock())
    # First call: LLM wants to call edit_file
    mock_generate.return_value = '{"thought": "edit", "tool": "edit_file", "args": {"path": "x", "old_string": "a", "new_string": "b"}}'
    messages = [{"role": "user", "content": "Change x"}]
    current, reply, pending, _ = run_loop(messages, agent_context, max_turns=3)
    assert reply is None
    assert pending is not None
    assert pending.get("tool") == "edit_file"


@patch("app.services.agent_kernel._get_llm")
def test_run_loop_no_llm_returns_error_message(mock_get_llm):
    mock_get_llm.return_value = (None, None)
    messages = [{"role": "user", "content": "Hi"}]
    current, reply, pending, err = run_loop(messages, {}, max_turns=2)
    assert "don't have an LLM" in (reply or "")
    assert err == "no_llm_configured"


# --- execute_pending_and_continue ---

@patch("app.services.agent_kernel._generate")
@patch("app.services.agent_kernel._get_llm")
def test_execute_pending_edit_then_continues(mock_get_llm, mock_generate, agent_context, tmp_workspace):
    (Path(tmp_workspace) / "fixme.txt").write_text("old line\n", encoding="utf-8")
    mock_get_llm.return_value = ("openai", MagicMock())
    mock_generate.return_value = '{"thought": "done", "reply": "Fixed."}'
    messages = [{"role": "user", "content": "Fix it"}]
    updated, reply, pending, _ = execute_pending_and_continue(
        messages, agent_context,
        approved_tool="edit_file",
        approved_args={"path": "fixme.txt", "old_string": "old line", "new_string": "new line"},
        max_turns_after=2,
    )
    assert len(updated) > len(messages)
    content = (Path(tmp_workspace) / "fixme.txt").read_text(encoding="utf-8")
    assert "new line" in content
    assert reply == "Fixed."


# --- workspace context block ---

def test_workspace_context_block_empty_without_root():
    block = _get_workspace_context_block({}, [])
    assert block == ""


def test_workspace_context_block_includes_list(agent_context):
    block = _get_workspace_context_block(agent_context, [])
    assert "Workspace context" in block
    assert "README" in block or "src" in block


def test_workspace_context_block_includes_search_when_user_message(agent_context):
    messages = [{"role": "user", "content": "where is the TODO"}]
    block = _get_workspace_context_block(agent_context, messages)
    assert "Workspace context" in block
