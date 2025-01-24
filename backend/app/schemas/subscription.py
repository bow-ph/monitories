from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionBase(BaseModel):
    user_id: int
    mollie_id: str
    customer_id: str
    package_id: int
    package_type: str
    project_limit: Optional[int]
    status: str
    amount: float
    interval: str
    start_date: datetime
    end_date: Optional[datetime]
    last_payment_date: Optional[datetime]
    next_payment_date: Optional[datetime]

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    status: Optional[str] = None
    project_limit: Optional[int] = None
    end_date: Optional[datetime] = None

class SubscriptionResponse(SubscriptionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
