from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionResponse, SubscriptionUpdate
from app.services.subscription_service import SubscriptionService
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's active subscription"""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_user_subscription(current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription

@router.get("/me/project-limit", response_model=Dict)
async def check_project_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user can create more projects"""
    subscription_service = SubscriptionService(db)
    return subscription_service.can_create_project(current_user.id)

@router.post("/me/cancel", response_model=Dict)
async def cancel_subscription(
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel current user's subscription"""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_user_subscription(current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    try:
        return subscription_service.cancel_subscription(subscription.id, reason)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
