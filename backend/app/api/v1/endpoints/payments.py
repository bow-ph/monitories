from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime
from app.core.database import get_db
from app.services.mollie_service import MollieService
from app.core.config import settings
from app.models.subscription import Subscription

router = APIRouter()

def get_mollie_service(db: Session = Depends(get_db)) -> MollieService:
    return MollieService(db)

@router.post("/customers")
async def create_customer(
    name: str,
    email: str,
    metadata: Optional[Dict] = None,
    db: Session = Depends(get_db),
    mollie_service: MollieService = Depends(get_mollie_service)
):
    """Create a new Mollie customer"""
    return await mollie_service.create_customer(name, email, metadata)

@router.post("/subscriptions/{customer_id}")
async def create_subscription(
    customer_id: str,
    amount: float,
    interval: str,
    description: str,
    db: Session = Depends(get_db),
    mollie_service: MollieService = Depends(get_mollie_service)
):
    """Create a subscription for a customer"""
    webhook_url = f"{settings.API_V1_STR}/payments/webhook"
    return await mollie_service.create_subscription(
        customer_id,
        amount,
        interval,
        description,
        webhook_url
    )

@router.get("/subscriptions/{customer_id}")
async def list_subscriptions(
    customer_id: str,
    db: Session = Depends(get_db),
    mollie_service: MollieService = Depends(get_mollie_service)
):
    """List all subscriptions for a customer"""
    return await mollie_service.list_subscriptions(customer_id)

@router.get("/subscriptions/{customer_id}/{subscription_id}")
async def get_subscription(
    customer_id: str,
    subscription_id: str,
    db: Session = Depends(get_db),
    mollie_service: MollieService = Depends(get_mollie_service)
):
    """Get subscription details"""
    return await mollie_service.get_subscription(customer_id, subscription_id)

@router.delete("/subscriptions/{customer_id}/{subscription_id}")
async def cancel_subscription(
    customer_id: str,
    subscription_id: str,
    db: Session = Depends(get_db),
    mollie_service: MollieService = Depends(get_mollie_service)
):
    """Cancel a subscription"""
    return await mollie_service.cancel_subscription(customer_id, subscription_id)

@router.post("/webhook")
async def handle_webhook(
    payment_id: str,
    db: Session = Depends(get_db),
    mollie_service: MollieService = Depends(get_mollie_service)
):
    """Handle webhook notification from Mollie"""
    try:
        result = await mollie_service.handle_webhook(payment_id)
        
        # Update subscription status in database
        if result["subscription_id"]:
            subscription = db.query(Subscription).filter(
                Subscription.mollie_id == result["subscription_id"]
            ).first()
            
            if subscription:
                subscription.status = result["status"]
                if result["status"] == "paid":
                    subscription.last_payment_date = datetime.utcnow()
                db.commit()
        
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
