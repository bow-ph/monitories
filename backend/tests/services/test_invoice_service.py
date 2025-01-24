import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.services.invoice_service import InvoiceService
from app.models.invoice import Invoice
from app.models.user import User
from app.models.subscription import Subscription
from app.models.package import Package
import os

@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def invoice_service(db_session):
    return InvoiceService(db_session)

@pytest.fixture
def mock_package():
    return Package(
        id=1,
        name="Test Package",
        description="Test package description",
        price=119.0,
        interval="3 months",
        max_projects=10,
        features=["Feature 1", "Feature 2"],
        button_text="Get Test Package",
        is_active=True
    )

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        client_type="company",
        company_name="Test Corp",
        vat_number="DE123456789",
        billing_address="Test Street 1",
        is_active=True
    )

@pytest.fixture
def mock_subscription(mock_package):
    return Subscription(
        id=1,
        user_id=1,
        mollie_id="sub_test",
        customer_id="cust_test",
        package_id=mock_package.id,
        status="active",
        amount=mock_package.price,
        interval=mock_package.interval
    )

def test_generate_invoice_number(invoice_service, db_session):
    """Test unique invoice number generation"""
    today = datetime.now()
    year_month = today.strftime('%Y-%m')
    
    # Mock the query to return None for latest invoice
    db_session.query().filter().order_by().first.return_value = None
    
    invoice_number = invoice_service.generate_invoice_number()
    assert invoice_number == f"INV-{year_month}-0001"  # First invoice of the month
    
    # Mock an existing invoice to test sequence increment
    mock_invoice = MagicMock()
    mock_invoice.invoice_number = f"INV-{year_month}-0005"
    db_session.query().filter().order_by().first.return_value = mock_invoice
    
    invoice_number = invoice_service.generate_invoice_number()
    assert invoice_number == f"INV-{year_month}-0006"  # Next after 5 existing invoices

def test_create_invoice_with_vat(invoice_service, db_session, mock_user, mock_package, mock_subscription):
    """Test invoice creation with VAT calculation"""
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        client_type="company",
        company_name="Test Corp",
        vat_number="DE123456789",  # German VAT
        contact_person="Test Contact",
        billing_address="Test Address"
    )
    db_session.query(User).filter().first.return_value = mock_user
    db_session.query(Package).filter().first.return_value = mock_package
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    invoice = invoice_service.create_invoice(
        user_id=mock_user.id,
        subscription_id=mock_subscription.id,
        total_amount=119.0,
        net_amount=100.0,
        vat_amount=19.0,
        vat_rate=0.19,
        description="Test Invoice",
        currency="EUR",
        issue_date=datetime.now()
    )
    
    assert invoice.total_amount == 119.0
    assert invoice.net_amount == 100.0
    assert invoice.vat_amount == 19.0
    assert invoice.vat_rate == 0.19
    assert invoice.currency == "EUR"
    assert invoice.status == "pending"
    assert invoice.pdf_path.endswith(".pdf")

def test_create_invoice_without_vat(invoice_service, db_session, mock_user, mock_package, mock_subscription):
    """Test invoice creation without VAT for non-EU customers"""
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        client_type="private",
        vat_number=None,  # No VAT number
        contact_person="Test Contact",
        billing_address="Test Address"
    )
    db_session.query(User).filter().first.return_value = mock_user
    db_session.query(Package).filter().first.return_value = mock_package
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    invoice = invoice_service.create_invoice(
        user_id=mock_user.id,
        subscription_id=mock_subscription.id,
        total_amount=100.0,
        net_amount=100.0,
        vat_amount=0.0,
        vat_rate=0.0,
        description="Test Invoice",
        currency="EUR",
        issue_date=datetime.now()
    )
    
    assert invoice.total_amount == 100.0
    assert invoice.net_amount == 100.0
    assert invoice.vat_amount == 0.0
    assert invoice.vat_rate == 0.0
    assert invoice.currency == "EUR"
    assert invoice.status == "pending"
    assert invoice.pdf_path.endswith(".pdf")

def test_invoice_storage_path(invoice_service, tmp_path, mock_user, mock_package, mock_subscription):
    """Test invoice storage path creation"""
    storage_path = tmp_path / "invoices"
    invoice_service.invoice_dir = str(storage_path)
    
    # Create a mock user with required attributes
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        client_type="private",
        contact_person="Test Contact",
        billing_address="Test Address"
    )
    
    issue_date = datetime(2024, 1, 15)  # Fixed date for testing
    invoice = Invoice(
        id=1,
        invoice_number="2024-01-00001",
        user_id=mock_user.id,
        subscription_id=mock_subscription.id,
        total_amount=119.0,
        net_amount=100.0,
        vat_amount=19.0,
        vat_rate=0.19,
        currency="EUR",
        issue_date=issue_date
    )
    
    path = invoice_service._generate_pdf(invoice, mock_user, mock_subscription, "Test Invoice")
    expected_path = os.path.join(str(storage_path), "2024", "01", "2024-01-00001.pdf")
    assert path == expected_path
    assert os.path.exists(path)

def test_invoice_generation_error_handling(invoice_service, db_session, mock_user, mock_package, mock_subscription):
    """Test error handling during invoice generation"""
    # Create a mock user with required attributes
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        client_type="private",
        contact_person="Test Contact",
        billing_address="Test Address"
    )
    
    db_session.query(User).filter().first.return_value = mock_user
    db_session.query(Package).filter().first.return_value = mock_package
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    # Mock PDF generation error
    with patch('app.services.invoice_service.InvoiceService._generate_pdf', side_effect=Exception("PDF generation failed")):
        with pytest.raises(Exception) as exc_info:
            invoice_service.create_invoice(
                user_id=mock_user.id,
                subscription_id=mock_subscription.id,
                total_amount=119.0,
                net_amount=100.0,
                vat_amount=19.0,
                vat_rate=0.19,
                description="Test Invoice",
                currency="EUR",
                issue_date=datetime.now()
            )
        assert "PDF generation failed" in str(exc_info.value)
        
        # Verify transaction was rolled back
        db_session.rollback.assert_called_once()
