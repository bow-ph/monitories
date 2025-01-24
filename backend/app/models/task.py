from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    description = Column(String)
    estimated_hours = Column(Float)
    actual_hours = Column(Float, nullable=True)
    status = Column(String)  # pending, in_progress, completed
    priority = Column(String, nullable=True)  # high, medium, low
    confidence_score = Column(Float)  # AI confidence in the estimate (0-1)
    confidence_rationale = Column(String)  # Detailed explanation of confidence score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Monitoring-specific fields
    finding_type = Column(String, nullable=True)  # security, performance, update, compliance
    technical_details = Column(JSON, nullable=True)  # Component, current state, desired state
    risks = Column(JSON, nullable=True)  # List of potential risks
    severity = Column(String, nullable=True)  # low, medium, high, critical
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
