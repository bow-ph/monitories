from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.schemas.user import User as UserSchema, UserUpdate
from app.schemas.subscription import SubscriptionResponse, SubscriptionUpdate
from app.schemas.invoice import InvoiceResponse
from app.core.auth import get_current_user, require_superuser

router = APIRouter(tags=["admin"])

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_all_subscriptions(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Get all subscriptions with their details.
    Only accessible by superusers.
    """
    subscriptions = db.query(Subscription).all()
    return subscriptions

@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_all_invoices(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Get all invoices with their details.
    Only accessible by superusers.
    """
    invoices = db.query(Invoice).all()
    return invoices

@router.get("/users/{user_id}/subscriptions", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Get all subscriptions for a specific user.
    Only accessible by superusers.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    subscriptions = db.query(Subscription).filter(Subscription.user_id == user_id).all()
    return subscriptions

@router.get("/users/{user_id}/invoices", response_model=List[InvoiceResponse])
async def get_user_invoices(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Get all invoices for a specific user.
    Only accessible by superusers.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
    return invoices

@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    subscription_update: SubscriptionUpdate,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Update subscription details.
    Only accessible by superusers.
    """
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    for field, value in subscription_update.model_dump(exclude_unset=True).items():
        setattr(subscription, field, value)
    
    try:
        db.commit()
        db.refresh(subscription)
        return subscription
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating subscription: {str(e)}"
        )

@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Get all users with their details.
    Only accessible by superusers.
    """
    
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific user.
    Only accessible by superusers.
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user_details(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db)
):
    """
    Update user details including client information.
    Only accessible by superusers.
    """
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate input data
    if user_update.client_type not in ["private", "company"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid client type. Must be 'private' or 'company'"
        )
    
    if user_update.client_type == "company" and user_update.vat_number:
        if not user_update.vat_number.startswith("DE"):
            raise HTTPException(
                status_code=400,
                detail="VAT number must start with DE for German companies"
            )
    
    try:
        # Validate input data first
        if user_update.client_type not in ["private", "company"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid client type. Must be 'private' or 'company'"
            )
        
        if user_update.client_type == "company" and user_update.vat_number:
            if not user_update.vat_number.startswith("DE"):
                raise HTTPException(
                    status_code=400,
                    detail="VAT number must start with DE for German companies"
                )
        
        # Update user fields
        for field, value in user_update.model_dump(exclude_unset=True).items():
            if field != "id" and hasattr(db_user, field):  # Don't update id
                setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        # Convert SQLAlchemy model to dict
        return {
            "id": db_user.id,
            "email": db_user.email,
            "is_active": db_user.is_active,
            "client_type": db_user.client_type,
            "company_name": db_user.company_name,
            "vat_number": db_user.vat_number,
            "billing_address": db_user.billing_address,
            "shipping_address": db_user.shipping_address,
            "phone_number": db_user.phone_number,
            "contact_person": db_user.contact_person,
            "notes": db_user.notes,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error updating user: {str(e)}"
        )
