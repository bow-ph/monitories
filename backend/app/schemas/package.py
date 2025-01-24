from pydantic import BaseModel
from typing import List, Optional

class PackageBase(BaseModel):
    name: str
    description: str
    price: float
    interval: str = "3 months"
    trial_days: Optional[int] = None
    max_projects: int
    features: List[str]
    button_text: str
    sort_order: Optional[int] = 0
    is_active: bool = True

class PackageCreate(PackageBase):
    pass

class PackageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    interval: Optional[str] = None
    trial_days: Optional[int] = None
    max_projects: Optional[int] = None
    features: Optional[List[str]] = None
    button_text: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class Package(PackageBase):
    id: int

    class Config:
        from_attributes = True
