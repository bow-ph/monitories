from typing import Dict, Optional
from mollie.api.client import Client
from mollie.api.error import Error as MollieError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User

class MollieService:
    def __init__(self, db: Session):
        """Initialize Mollie client with API key based on mode"""
        self.db = db
        self.client = Client()
        self.client.set_api_key(
            settings.MOLLIE_LIVE_API_KEY if settings.MOLLIE_MODE == "live"
            else settings.MOLLIE_TEST_API_KEY
        )

    async def create_subscription(
        self,
        customer_id: str,
        amount: float,
        interval: str,
        description: str,
        webhook_url: str
    ) -> Dict:
        """Create a subscription for a customer"""
        try:
            subscription = self.client.customers.subscriptions.with_parent_id(
                customer_id
            ).create({
                "amount": {
                    "currency": "EUR",
                    "value": f"{amount:.2f}"
                },
                "interval": interval,
                "description": description,
                "webhookUrl": webhook_url
            })
            return subscription
        except MollieError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def create_customer(
        self,
        name: str,
        email: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a new Mollie customer"""
        try:
            customer = self.client.customers.create({
                "name": name,
                "email": email,
                "metadata": metadata or {}
            })
            return customer
        except MollieError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_subscription(self, customer_id: str, subscription_id: str) -> Dict:
        """Get subscription details"""
        try:
            subscription = self.client.customer_subscriptions.with_parent_id(
                customer_id
            ).get(subscription_id)
            return subscription
        except MollieError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def cancel_subscription(self, customer_id: str, subscription_id: str) -> Dict:
        """Cancel a subscription and send notification email"""
        try:
            subscription = self.client.customers.subscriptions.with_parent_id(
                customer_id
            ).delete(subscription_id)
            
            # Send cancellation email
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            # Get customer details
            customer = self.client.customers.get(customer_id)
            
            # Send cancellation confirmation
            email_service.send_subscription_cancellation(
                customer.email,
                subscription.get("description", "Unknown Package")
            )
            
            return subscription
        except MollieError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def handle_webhook(self, payment_id: str) -> Dict:
        """Handle webhook notification from Mollie"""
        try:
            payment = self.client.payments.get(payment_id)
            result = {
                "status": payment.status,
                "amount": payment.amount,
                "customer_id": payment.customer_id,
                "subscription_id": payment.subscription_id,
                "metadata": payment.metadata
            }
            
            if payment.is_paid():
                # Create invoice
                from app.services.invoice_service import InvoiceService
                from app.services.email_service import EmailService
                
                invoice_service = InvoiceService(self.db)
                email_service = EmailService()
                
                # Get package details from metadata
                package_name = payment.metadata.get("package_name", "Unknown Package")
                amount = float(payment.amount["value"])
                
                try:
                    # Get user for VAT calculation
                    user = self.db.query(User).filter(
                        User.id == payment.metadata.get("user_id")
                    ).first()
                    
                    if not user:
                        raise ValueError("User not found")
                    
                    # Calculate VAT (19% for German clients)
                    vat_rate = 0.19 if user.vat_number and user.vat_number.startswith("DE") else 0.0
                    net_amount = amount / (1 + vat_rate) if vat_rate > 0 else amount
                    vat_amount = amount - net_amount if vat_rate > 0 else 0.0
                    
                    # Create invoice with VAT information
                    invoice = invoice_service.create_invoice(
                        user_id=user.id,
                        subscription_id=payment.subscription_id,
                        total_amount=amount,
                        net_amount=net_amount,
                        vat_amount=vat_amount,
                        vat_rate=vat_rate,
                        description=f"Subscription payment for {package_name}",
                        currency="EUR"
                    )
                    
                    # Send confirmation email with invoice
                    email_service.send_payment_confirmation(
                        payment.metadata.get("email"),
                        package_name,
                        amount,
                        invoice.pdf_path
                    )
                    
                    result.update({
                        "status": "paid",
                        "invoice_number": invoice.invoice_number,
                        "invoice_path": invoice.pdf_path
                    })
                except Exception as e:
                    print(f"Error generating invoice: {str(e)}")
                    result["status"] = "paid_no_invoice"
            elif payment.is_failed():
                result["status"] = "failed"
            
            return result
            
        except MollieError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def list_subscriptions(self, customer_id: str) -> Dict:
        """List all subscriptions for a customer"""
        try:
            subscriptions = self.client.customers.subscriptions.with_parent_id(
                customer_id
            ).list()
            return subscriptions
        except MollieError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_subscription(
        self,
        customer_id: str,
        subscription_id: str,
        amount: Optional[float] = None,
        interval: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """Update subscription details"""
        try:
            data = {}
            if amount is not None:
                data["amount"] = {
                    "currency": "EUR",
                    "value": f"{amount:.2f}"
                }
            if interval is not None:
                data["interval"] = interval
            if description is not None:
                data["description"] = description

            subscription = self.client.customer_subscriptions.with_parent_id(
                customer_id
            ).update(subscription_id, data)
            return subscription
        except MollieError as e:
            raise HTTPException(status_code=400, detail=str(e))
