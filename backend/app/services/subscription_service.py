from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.models.project import Project
from app.models.user import User
from app.services.email_service import EmailService

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
    
    def can_create_project(self, user_id: int) -> Dict:
        """Check if user can create a new project based on their subscription"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()
        
        if not subscription:
            return {
                "can_create": False,
                "reason": "No active subscription found"
            }
            
        # Check if subscription is expired
        if subscription.end_date and subscription.end_date < datetime.now():
            return {
                "can_create": False,
                "reason": "Subscription has expired"
            }
            
        # Get current project count in subscription period
        project_count = self.db.query(Project).filter(
            Project.user_id == user_id,
            Project.created_at >= subscription.start_date,
            Project.created_at <= (subscription.end_date or datetime.max)
        ).count()
        
        # Check limits based on package type
        if subscription.package_type == "trial":
            can_create = project_count < 1
            return {
                "can_create": can_create,
                "current_count": project_count,
                "limit": 1,
                "reason": "Trial limited to 1 project" if not can_create else None
            }
        elif subscription.package_type == "team":
            can_create = project_count < 10
            return {
                "can_create": can_create,
                "current_count": project_count,
                "limit": 10,
                "reason": "Team plan limited to 10 projects" if not can_create else None
            }
        elif subscription.package_type == "enterprise":
            # Use custom limit if set, otherwise unlimited
            if subscription.project_limit is not None:
                can_create = project_count < subscription.project_limit
                return {
                    "can_create": can_create,
                    "current_count": project_count,
                    "limit": subscription.project_limit,
                    "reason": f"Enterprise plan limited to {subscription.project_limit} projects" if not can_create else None
                }
            return {
                "can_create": True,
                "current_count": project_count,
                "limit": None,
                "reason": None
            }
            
        return {
            "can_create": False,
            "reason": "Invalid subscription type"
        }
    
    def get_package_duration(self, package_type: str, custom_months: Optional[int] = None) -> timedelta:
        """Get subscription duration based on package type"""
        if package_type in ["trial", "team"]:
            return timedelta(days=90)  # 3 months
        elif package_type == "enterprise":
            # Default to 12 months for enterprise if not specified
            months = custom_months if custom_months is not None else 12
            return timedelta(days=int(months * 30.44))  # Average month length
        else:
            raise ValueError("Invalid package type")
            
    def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        return self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get active subscription for user"""
        return (
            self.db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == "active"
            )
            .first()
        )
    
    def cancel_subscription(self, subscription_id: int, reason: Optional[str] = None) -> Dict:
        """Cancel a subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")
            
        if subscription.status != "active":
            raise ValueError("Subscription is not active")
            
        try:
            # Update subscription status
            subscription.status = "cancelled"
            subscription.end_date = datetime.now() + timedelta(days=90)  # 3 months notice
            self.db.commit()
            
            # Send cancellation email
            user = self.db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                self.email_service.send_subscription_cancellation(
                    user.email,
                    subscription.package_type
                )
            
            return {
                "status": "success",
                "message": "Subscription cancelled successfully",
                "end_date": subscription.end_date.isoformat()
            }
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error cancelling subscription: {str(e)}")
    
    def check_subscription_expiry(self) -> List[Dict]:
        """Check for subscriptions nearing expiry and send notifications"""
        expiring_soon = []
        
        subscriptions = (
            self.db.query(Subscription)
            .filter(
                Subscription.status == "active",
                Subscription.end_date.isnot(None)
            )
            .all()
        )
        
        for subscription in subscriptions:
            if not subscription.end_date:
                continue
                
            days_left = (subscription.end_date - datetime.now()).days
            
            if days_left <= 30:  # Notify when 30 days or less remaining
                user = self.db.query(User).filter(User.id == subscription.user_id).first()
                if user:
                    self.email_service.send_subscription_expiry_notice(
                        user.email,
                        days_left
                    )
                    expiring_soon.append({
                        "subscription_id": subscription.id,
                        "user_id": user.id,
                        "email": user.email,
                        "days_left": days_left
                    })
                    
        return expiring_soon
