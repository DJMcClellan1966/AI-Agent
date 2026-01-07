from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime


class IntegrationBase(BaseModel):
    integration_type: str
    provider: str
    name: str
    config: Optional[Dict] = {}


class IntegrationCreate(IntegrationBase):
    pass


class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict] = None
    status: Optional[str] = None


class IntegrationResponse(IntegrationBase):
    id: int
    user_id: int
    status: str
    permissions: List
    last_sync: Optional[datetime]
    sync_interval_minutes: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
