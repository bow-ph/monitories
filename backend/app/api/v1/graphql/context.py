from typing import Any, Dict
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

async def get_context(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return {
        "request": request,
        "db": db,
        "user": current_user
    }
