"""
Agent chat endpoint: run the agent kernel (LLM + tools) and return the reply.
Supports human-in-the-loop for edit_file and run_terminal.
"""
import os
from fastapi import APIRouter, Depends

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


@router.get("/config")
def agent_config(current_user: User = Depends(get_current_active_user)):
    """Return server-side defaults for CodeLearn/CodeIQ so the UI can pre-fill. No secrets."""
    return {
        "codelearn_guidance_url": (os.environ.get("CODELEARN_GUIDANCE_URL") or "").strip(),
        "codeiq_workspace": (os.environ.get("CODEIQ_WORKSPACE") or "").strip(),
    }


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
    updated_messages, reply, pending = run_loop(
        messages=messages,
        context=context,
        max_turns=5,
    )
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
    updated_messages, reply, pending = execute_pending_and_continue(
        messages=messages,
        context=context,
        approved_tool=body.tool,
        approved_args=body.args,
    )
    return AgentChatResponse(
        reply=reply,
        messages=updated_messages,
        pending_approval=_pending_to_schema(pending) if pending else None,
    )
