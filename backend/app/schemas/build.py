from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class BuildMessage(BaseModel):
    role: str  # "user" | "system"
    content: str


class BuildGenerateRequest(BaseModel):
    """Request to generate an app from conversation."""
    messages: List[BuildMessage] = Field(..., description="Conversation history")
    project_name: Optional[str] = Field(None, description="Optional project name override")


class SuggestQuestionRequest(BaseModel):
    """Request for suggested follow-up questions."""
    messages: List[BuildMessage] = Field(..., description="Conversation history so far")


class SuggestQuestionResponse(BaseModel):
    """1–2 suggested follow-up questions for the conversation."""
    questions: List[str] = Field(..., description="Suggested questions the user could answer")


class ProjectSpec(BaseModel):
    """Structured spec extracted from conversation."""
    name: str = "MyApp"
    type: str = "app"  # dashboard, tracker, notes, todo, library, app
    features: List[str] = Field(default_factory=list)
    persistence: str = "localStorage"  # localStorage, session, none
    theme: str = "dark"  # light, dark, system
    ui_complexity: str = "minimal"  # minimal, rich


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    spec: Dict[str, Any]
    files: Dict[str, str]
    conversation_summary: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
