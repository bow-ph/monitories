from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    subscription_type = Column(String, nullable=True)  # trial, team, enterprise
    subscription_end_date = Column(DateTime, nullable=True)
    
    # Client information
    client_type = Column(String, default="private")  # private or company
    company_name = Column(String, nullable=True)  # Company name for business clients
    vat_number = Column(String, nullable=True)  # VAT/Tax ID for billing
    billing_address = Column(String, nullable=True)  # Primary billing address
    shipping_address = Column(String, nullable=True)  # Optional different shipping address
    phone_number = Column(String, nullable=True)  # Contact phone number
    contact_person = Column(String, nullable=True)  # Primary contact for company clients
    notes = Column(String, nullable=True)  # Admin notes about the client
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    invoices = relationship("Invoice", back_populates="user")
    projects = relationship("Project", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
