"""
Agent chat endpoint: run the agent kernel (LLM + tools) and return the reply.
Supports human-in-the-loop for edit_file and run_terminal.
"""
from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.core.security import get_current_active_user
from app.schemas.agent_chat import (
    AgentChatRequest,
    AgentChatResponse,
    ExecutePendingRequest,
    PendingApproval,
)
from app.services.agent_kernel import run_loop, execute_pending_and_continue

router = APIRouter()


def _error_response(error_code: str, detail: str, status_code: int):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "type": error_code},
    )


@router.get("/config")
def agent_config(current_user: User = Depends(get_current_active_user)):
    """Minimal config for the agent UI (no external integrations)."""
    return {}


def _pending_to_schema(p: dict):
    if not p or not p.get("tool"):
        return None
    return PendingApproval(tool=p["tool"], args=p.get("args") or {}, preview=p.get("preview") or "")


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(
    body: AgentChatRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Send messages to the agent. The agent can use tools; edit_file and run_terminal
    require approval (response will have pending_approval). Pass context.workspace_root for file tools.
    """
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    context = body.context or {}
    updated_messages, reply, pending, error_code = run_loop(
        messages=messages,
        context=context,
        max_turns=5,
    )
    if error_code == "no_llm_configured":
        raise _error_response(error_code, reply or "No LLM configured.", status.HTTP_503_SERVICE_UNAVAILABLE)
    if error_code == "workspace_not_allowed":
        raise _error_response(error_code, reply or "Workspace not allowed.", status.HTTP_400_BAD_REQUEST)
    if error_code == "agent_timeout":
        raise _error_response(error_code, reply or "Agent timed out.", status.HTTP_408_REQUEST_TIMEOUT)
    return AgentChatResponse(
        reply=reply,
        messages=updated_messages,
        pending_approval=_pending_to_schema(pending) if pending else None,
    )


@router.post("/execute-pending", response_model=AgentChatResponse)
def execute_pending(
    body: ExecutePendingRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Execute an approved edit_file or run_terminal and continue the agent."""
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    context = body.context or {}
    updated_messages, reply, pending, error_code = execute_pending_and_continue(
        messages=messages,
        context=context,
        approved_tool=body.tool,
        approved_args=body.args,
    )
    if error_code == "no_llm_configured":
        return _error_response(error_code, reply or "No LLM configured.", status.HTTP_503_SERVICE_UNAVAILABLE)
    if error_code == "workspace_not_allowed":
        return _error_response(error_code, reply or "Workspace not allowed.", status.HTTP_400_BAD_REQUEST)
    if error_code == "agent_timeout":
        return _error_response(error_code, reply or "Agent timed out.", status.HTTP_408_REQUEST_TIMEOUT)
    return AgentChatResponse(
        reply=reply,
        messages=updated_messages,
        pending_approval=_pending_to_schema(pending) if pending else None,
    )
