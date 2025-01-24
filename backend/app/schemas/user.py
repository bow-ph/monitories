from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    two_factor_enabled: Optional[bool] = False
    subscription_type: Optional[str] = None
    subscription_end_date: Optional[datetime] = None
    
    # Client information
    client_type: Optional[str] = "private"  # private or company
    company_name: Optional[str] = None  # Company name for business clients
    vat_number: Optional[str] = None  # VAT/Tax ID for billing
    billing_address: Optional[str] = None  # Primary billing address
    shipping_address: Optional[str] = None  # Optional different shipping address
    phone_number: Optional[str] = None  # Contact phone number
    contact_person: Optional[str] = None  # Primary contact for company clients
    notes: Optional[str] = None  # Admin notes about the client

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None
    subscription_type: Optional[str] = None
    subscription_end_date: Optional[datetime] = None
    
    # Client information
    client_type: Optional[str] = None
    company_name: Optional[str] = None
    vat_number: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    phone_number: Optional[str] = None
    contact_person: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
