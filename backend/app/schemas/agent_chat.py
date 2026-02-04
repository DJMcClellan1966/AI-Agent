from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class AgentMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class AgentChatRequest(BaseModel):
    """Request to run the agent (one user message or full history)."""
    messages: List[AgentMessage] = Field(..., description="Conversation so far (user + assistant)")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional: workspace_root path, etc.")


class PendingApproval(BaseModel):
    """Human-in-the-loop: agent wants to run a tool; user must approve."""
    tool: str = Field(..., description="Tool name (edit_file, run_terminal)")
    args: Dict[str, Any] = Field(..., description="Tool arguments")
    preview: str = Field(..., description="Diff or command preview to show the user")


class AgentChatResponse(BaseModel):
    """Agent reply and updated conversation."""
    reply: Optional[str] = Field(None, description="Final reply to show the user; null when pending_approval is set")
    messages: List[Dict[str, str]] = Field(..., description="Full conversation including tool turns (for debugging or persistence)")
    pending_approval: Optional[PendingApproval] = Field(None, description="When set, user must approve before continuing")


class ExecutePendingRequest(BaseModel):
    """Execute a previously approved tool and continue the agent."""
    messages: List[AgentMessage] = Field(..., description="Full conversation so far (as returned by /chat)")
    context: Optional[Dict[str, Any]] = Field(None, description="Same context as chat (e.g. workspace_root)")
    tool: str = Field(..., description="Tool name (edit_file, run_terminal)")
    args: Dict[str, Any] = Field(..., description="Tool arguments (path, old_string, new_string or command, cwd)")
