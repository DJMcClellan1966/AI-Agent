"""
Tests for agent chat API: /api/v1/agent/config, /chat, /execute-pending.
Uses dependency override for auth and mocks run_loop/execute_pending_and_continue.
Skips entire module if full app cannot be imported (e.g. no DB driver).
"""
from unittest.mock import patch, MagicMock

import pytest

try:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.security import get_current_active_user
    _AGENT_CHAT_API_AVAILABLE = True
except Exception:
    _AGENT_CHAT_API_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AGENT_CHAT_API_AVAILABLE,
    reason="App main (e.g. DB) not available; skip agent chat API tests",
)


def _mock_user():
    u = MagicMock()
    u.id = 1
    u.email = "test@example.com"
    u.username = "testuser"
    u.is_active = True
    return u


@pytest.fixture
def client_with_auth():
    """TestClient with get_current_active_user overridden to return a mock user."""
    async def override_get_current_active_user():
        return _mock_user()

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


# --- GET /api/v1/agent/config ---

def test_agent_config_returns_ok(client_with_auth):
    r = client_with_auth.get("/api/v1/agent/config")
    assert r.status_code == 200
    data = r.json()
    assert "codelearn_guidance_url" in data
    assert "codeiq_workspace" in data


def test_agent_config_values_are_strings(client_with_auth):
    r = client_with_auth.get("/api/v1/agent/config")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["codelearn_guidance_url"], str)
    assert isinstance(data["codeiq_workspace"], str)


# --- POST /api/v1/agent/chat ---

@patch("app.api.v1.agent_chat.run_loop")
def test_agent_chat_success(mock_run_loop, client_with_auth):
    mock_run_loop.return_value = (
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ],
        "Hi there!",
        None,
    )
    r = client_with_auth.post(
        "/api/v1/agent/chat",
        json={
            "messages": [{"role": "user", "content": "Hello"}],
            "context": {},
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["reply"] == "Hi there!"
    assert len(data["messages"]) == 2
    assert data["pending_approval"] is None
    mock_run_loop.assert_called_once()
    call_kw = mock_run_loop.call_args[1]
    assert call_kw["max_turns"] == 5


@patch("app.api.v1.agent_chat.run_loop")
def test_agent_chat_passes_context(mock_run_loop, client_with_auth):
    mock_run_loop.return_value = ([], "OK", None)
    client_with_auth.post(
        "/api/v1/agent/chat",
        json={
            "messages": [{"role": "user", "content": "List files"}],
            "context": {"workspace_root": "/some/path"},
        },
    )
    mock_run_loop.assert_called_once()
    assert mock_run_loop.call_args[1]["context"] == {"workspace_root": "/some/path"}


@patch("app.api.v1.agent_chat.run_loop")
def test_agent_chat_pending_approval(mock_run_loop, client_with_auth):
    mock_run_loop.return_value = (
        [{"role": "user", "content": "Edit file"}, {"role": "assistant", "content": ""}],
        None,
        {"tool": "edit_file", "args": {"path": "x", "old_string": "a", "new_string": "b"}, "preview": "diff..."},
    )
    r = client_with_auth.post(
        "/api/v1/agent/chat",
        json={
            "messages": [{"role": "user", "content": "Edit file"}],
            "context": None,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["reply"] is None
    assert data["pending_approval"] is not None
    assert data["pending_approval"]["tool"] == "edit_file"
    assert data["pending_approval"]["args"]["path"] == "x"
    assert "diff" in data["pending_approval"]["preview"]


@patch("app.api.v1.agent_chat.run_loop")
def test_agent_chat_empty_messages(mock_run_loop, client_with_auth):
    mock_run_loop.return_value = ([], "No input.", None)
    r = client_with_auth.post(
        "/api/v1/agent/chat",
        json={"messages": [], "context": None},
    )
    assert r.status_code == 200
    mock_run_loop.assert_called_once()
    assert mock_run_loop.call_args[1]["messages"] == []


# --- POST /api/v1/agent/execute-pending ---

@patch("app.api.v1.agent_chat.execute_pending_and_continue")
def test_execute_pending_success(mock_execute, client_with_auth):
    mock_execute.return_value = (
        [
            {"role": "user", "content": "Run ls"},
            {"role": "assistant", "content": ""},
            {"role": "assistant", "content": "Done. Listed files."},
        ],
        "Done. Listed files.",
        None,
    )
    r = client_with_auth.post(
        "/api/v1/agent/execute-pending",
        json={
            "messages": [{"role": "user", "content": "Run ls"}, {"role": "assistant", "content": ""}],
            "context": {"workspace_root": "/tmp"},
            "tool": "run_terminal",
            "args": {"command": "ls", "cwd": "/tmp"},
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["reply"] == "Done. Listed files."
    assert data["pending_approval"] is None
    mock_execute.assert_called_once()
    call_kw = mock_execute.call_args[1]
    assert call_kw["approved_tool"] == "run_terminal"
    assert call_kw["approved_args"]["command"] == "ls"


@patch("app.api.v1.agent_chat.execute_pending_and_continue")
def test_execute_pending_returns_new_pending(mock_execute, client_with_auth):
    mock_execute.return_value = (
        [{"role": "user", "content": "Edit a and b"}, {"role": "assistant", "content": ""}],
        None,
        {"tool": "edit_file", "args": {"path": "b", "old_string": "x", "new_string": "y"}, "preview": "next diff"},
    )
    r = client_with_auth.post(
        "/api/v1/agent/execute-pending",
        json={
            "messages": [{"role": "user", "content": "Edit a and b"}, {"role": "assistant", "content": ""}],
            "context": {},
            "tool": "edit_file",
            "args": {"path": "a", "old_string": "1", "new_string": "2"},
        },
    )
    assert r.status_code == 200
    assert r.json()["pending_approval"]["tool"] == "edit_file"
    assert r.json()["pending_approval"]["args"]["path"] == "b"


# --- Auth: without override, agent endpoints require auth (smoke check) ---

def test_agent_config_requires_auth():
    """Without dependency override, config endpoint should require valid token (401/403)."""
    app.dependency_overrides.pop(get_current_active_user, None)
    try:
        with TestClient(app) as c:
            r = c.get("/api/v1/agent/config")
            assert r.status_code in (401, 403)
    finally:
        # Restore so other tests can override again
        pass
