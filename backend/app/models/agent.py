from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class AgentType(str, enum.Enum):
    EMAIL = "email"
    SCHEDULER = "scheduler"
    FINANCE = "finance"
    PLANNING = "planning"
    COORDINATOR = "coordinator"
    CUSTOM = "custom"


class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Agent details
    agent_type = Column(Enum(AgentType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE)
    
    # Configuration
    config = Column(JSON, default={})
    permissions = Column(JSON, default={})
    
    # Capabilities
    can_execute_autonomously = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    max_daily_tasks = Column(Integer, default=10)
    
    # Metrics
    tasks_completed = Column(Integer, default=0)
    tasks_pending = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    success_rate = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
