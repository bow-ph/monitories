from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mollie_id = Column(String, unique=True, index=True)
    customer_id = Column(String)
    package_id = Column(Integer, ForeignKey("packages.id"))
    package_type = Column(String)  # trial, team, enterprise
    project_limit = Column(Integer, nullable=True)  # Custom limit for enterprise packages
    status = Column(String)  # active, pending, canceled, suspended
    amount = Column(Float)
    interval = Column(String)  # 3 months, 6 months, 12 months
    created_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    last_payment_date = Column(DateTime, nullable=True)
    next_payment_date = Column(DateTime, nullable=True)

    # Relationships
    invoices = relationship("Invoice", back_populates="subscription")
    user = relationship("User", back_populates="subscriptions")
    package = relationship("Package", back_populates="subscriptions")
