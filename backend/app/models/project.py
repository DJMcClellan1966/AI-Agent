from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Project(Base):
    """Generated app project from conversational build."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String(255), nullable=False)
    """Project/app name."""
    spec = Column(JSON, default=dict)
    """Structured spec: type, features, persistence, theme, etc."""
    files = Column(JSON, default=dict)
    """Generated files: { "index.html": "...", "styles.css": "...", "app.js": "..." }."""
    conversation_summary = Column(Text, nullable=True)
    """Short summary of the conversation that led to this project."""

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="projects")
