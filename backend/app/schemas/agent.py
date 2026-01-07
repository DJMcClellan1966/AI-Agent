from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class AgentBase(BaseModel):
    agent_type: str
    name: str
    description: Optional[str] = None
    config: Optional[Dict] = {}
    permissions: Optional[Dict] = {}
    can_execute_autonomously: bool = False
    requires_approval: bool = True
    max_daily_tasks: int = 10


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict] = None
    permissions: Optional[Dict] = None
    can_execute_autonomously: Optional[bool] = None
    requires_approval: Optional[bool] = None
    max_daily_tasks: Optional[int] = None
    status: Optional[str] = None


class AgentResponse(AgentBase):
    id: int
    user_id: int
    status: str
    tasks_completed: int
    tasks_pending: int
    tasks_failed: int
    success_rate: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_active: Optional[datetime]
    
    class Config:
        from_attributes = True
