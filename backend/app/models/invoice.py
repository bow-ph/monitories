from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    issue_date = Column(DateTime, default=datetime.utcnow)
    
    # Financial information
    total_amount = Column(Float)  # Total amount including VAT
    net_amount = Column(Float)    # Amount without VAT
    vat_amount = Column(Float)    # VAT amount
    vat_rate = Column(Float)      # VAT rate used (e.g., 0.19 for 19%)
    currency = Column(String, default="EUR")
    
    pdf_path = Column(String)  # Path to stored PDF invoice
    status = Column(String, default="pending")  # pending, paid, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
