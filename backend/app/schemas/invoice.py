from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InvoiceBase(BaseModel):
    invoice_number: str
    user_id: int
    subscription_id: int
    total_amount: float
    pdf_path: Optional[str] = None
    status: str = "pending"

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    pdf_path: Optional[str] = None
    status: Optional[str] = None

class Invoice(InvoiceBase):
    id: int
    issue_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
