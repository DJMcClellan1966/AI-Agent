from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class IntegrationType(str, enum.Enum):
    EMAIL = "email"
    CALENDAR = "calendar"
    BANKING = "banking"
    COMMUNICATION = "communication"
    STORAGE = "storage"
    OTHER = "other"


class IntegrationStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"


class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Integration details
    integration_type = Column(Enum(IntegrationType), nullable=False)
    provider = Column(String, nullable=False)  # e.g., "gmail", "outlook", "google_calendar"
    name = Column(String, nullable=False)
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.PENDING)
    
    # Authentication
    access_token = Column(Text, nullable=True)  # Should be encrypted
    refresh_token = Column(Text, nullable=True)  # Should be encrypted
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    config = Column(JSON, default={})
    permissions = Column(JSON, default=[])
    
    # Sync status
    last_sync = Column(DateTime(timezone=True), nullable=True)
    sync_interval_minutes = Column(Integer, default=15)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="integrations")


class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Preferences
    key = Column(String, nullable=False)
    value = Column(JSON, nullable=False)
    category = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")
