from sqlalchemy import Column, Integer, String, Float, Boolean, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Float)
    interval = Column(String, default="3 months")  # Billing interval
    trial_days = Column(Integer, nullable=True)
    max_projects = Column(Integer)
    features = Column(ARRAY(String))
    is_active = Column(Boolean, default=True)
    button_text = Column(String)
    sort_order = Column(Integer, default=0)  # For controlling display order

    # Relationships
    subscriptions = relationship("Subscription", back_populates="package")
