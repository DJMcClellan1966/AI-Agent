from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str
    priority: str = "medium"
    input_data: Optional[Dict] = {}
    requires_approval: bool = True
    scheduled_for: Optional[datetime] = None
    deadline: Optional[datetime] = None


class TaskCreate(TaskBase):
    agent_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    deadline: Optional[datetime] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    agent_id: int
    status: str
    output_data: Optional[Dict]
    task_metadata: Optional[Dict] = Field(default=None, serialization_alias="metadata")
    approved_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
