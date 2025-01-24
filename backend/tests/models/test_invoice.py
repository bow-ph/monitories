import pytest
from datetime import datetime
from app.models.invoice import Invoice
from app.models.user import User
from app.models.subscription import Subscription

def test_create_invoice(db_session):
    # Create test user
    user = User(
        email="test@example.com",
        hashed_password="test",
        is_active=True,
        client_type="private"
    )
    db_session.add(user)
    db_session.flush()

    # Create test subscription
    subscription = Subscription(
        user_id=user.id,
        mollie_id="test_mollie_id",
        customer_id="test_customer",
        package_id=1,
        status="active",
        amount=99.99,
        interval="3 months"
    )
    db_session.add(subscription)
    db_session.flush()

    # Create test invoice
    invoice = Invoice(
        invoice_number="INV-2024-001",
        user_id=user.id,
        subscription_id=subscription.id,
        total_amount=99.99,
        pdf_path="/path/to/invoice.pdf",
        status="pending"
    )
    db_session.add(invoice)
    db_session.commit()

    # Verify invoice was created
    saved_invoice = db_session.query(Invoice).filter_by(id=invoice.id).first()
    assert saved_invoice is not None
    assert saved_invoice.invoice_number == "INV-2024-001"
    assert saved_invoice.total_amount == 99.99
    assert saved_invoice.status == "pending"
    assert saved_invoice.user_id == user.id
    assert saved_invoice.subscription_id == subscription.id

    # Test relationships
    assert saved_invoice.user.email == "test@example.com"
    assert saved_invoice.subscription.mollie_id == "test_mollie_id"

def test_invoice_status_update(db_session):
    # Create test invoice with relationships
    user = User(
        email="test@example.com",
        hashed_password="test",
        is_active=True,
        client_type="private"
    )
    db_session.add(user)
    
    subscription = Subscription(
        user_id=user.id,
        mollie_id="test_mollie_id",
        customer_id="test_customer",
        package_id=1,
        status="active",
        amount=99.99,
        interval="3 months"
    )
    db_session.add(subscription)
    
    invoice = Invoice(
        invoice_number="INV-2024-002",
        user_id=user.id,
        subscription_id=subscription.id,
        total_amount=99.99,
        status="pending"
    )
    db_session.add(invoice)
    db_session.commit()

    # Update invoice status
    invoice.status = "paid"
    db_session.commit()

    # Verify status update
    updated_invoice = db_session.query(Invoice).filter_by(id=invoice.id).first()
    assert updated_invoice.status == "paid"

def test_invoice_timestamps(db_session):
    # Create test invoice
    user = User(
        email="test@example.com",
        hashed_password="test",
        is_active=True,
        client_type="private"
    )
    db_session.add(user)
    
    subscription = Subscription(
        user_id=user.id,
        mollie_id="test_mollie_id",
        customer_id="test_customer",
        package_id=1,
        status="active",
        amount=99.99,
        interval="3 months"
    )
    db_session.add(subscription)
    
    invoice = Invoice(
        invoice_number="INV-2024-003",
        user_id=user.id,
        subscription_id=subscription.id,
        total_amount=99.99,
        status="pending"
    )
    db_session.add(invoice)
    db_session.commit()

    # Verify timestamps
    assert isinstance(invoice.created_at, datetime)
    assert isinstance(invoice.issue_date, datetime)
    
    # Update invoice to test updated_at
    invoice.status = "paid"
    db_session.commit()
    
    assert isinstance(invoice.updated_at, datetime)
    assert invoice.updated_at > invoice.created_at
