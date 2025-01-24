import pytest
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.auth import get_password_hash, create_access_token, get_current_user
from app.models.user import User
from app.models.package import Package
from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.task import Task
from fastapi.testclient import TestClient
from app.main import app

# Test database URL
SQLALCHEMY_DATABASE_URL = "postgresql://pmtool:pmtool@localhost/pmtool_test"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client(db_session, test_user):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    def override_get_current_user():
        return test_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def admin_user(db_session):
    """Create an admin user and return with token"""
    # Clean up any existing admin user
    db_session.query(User).filter(User.email == "admin@example.com").delete()
    db_session.commit()
    
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        client_type="private",
        notes="Admin user for testing",
        contact_person="Admin Test",
        phone_number="+1234567890",
        billing_address="Test Street 1\n12345 Test City",
        shipping_address="Test Street 1\n12345 Test City"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "user": user,
        "token": access_token
    }

@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a regular test user"""
    # Clean up any existing test users
    db_session.query(User).filter(User.email.like("test%@example.com")).delete()
    db_session.commit()
    
    # Generate unique email for this test run
    test_email = f"test_{int(datetime.now().timestamp())}@example.com"
    
    user = User(
        email=test_email,
        hashed_password=get_password_hash("testpass"),
        is_active=True,
        client_type="private",
        notes="Important client",
        contact_person="John Doe",
        phone_number="+1234567890",
        billing_address="Test Street 2\n12345 Test City",
        shipping_address="Test Street 2\n12345 Test City"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    yield user
    
    # Cleanup after test
    # Delete in order of dependencies: tasks -> projects -> user
    db_session.query(Task).filter(
        Task.project_id.in_(
            db_session.query(Project.id).filter(Project.user_id == user.id)
        )
    ).delete(synchronize_session=False)
    db_session.commit()
    
    db_session.query(Project).filter(Project.user_id == user.id).delete()
    db_session.commit()
    
    db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_company_user(db_session):
    """Create a company test user"""
    # Clean up any existing company users
    db_session.query(User).filter(User.email.like("company%@example.com")).delete()
    db_session.commit()
    
    # Generate unique email for this test run
    test_email = f"company_{int(datetime.now().timestamp())}@example.com"
    
    user = User(
        email=test_email,
        hashed_password=get_password_hash("testpass"),
        is_active=True,
        client_type="company",
        company_name="Test Corp",
        vat_number="DE123456789",
        notes="Company test user",
        contact_person="Company Test",
        phone_number="+1234567890",
        billing_address="Company Street 1\n12345 Business City",
        shipping_address="Company Street 1\n12345 Business City"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    yield user
    
    # Cleanup after test
    # First delete projects to avoid foreign key constraint violations
    db_session.query(Project).filter(Project.user_id == user.id).delete()
    db_session.commit()
    
    # Then delete the user
    db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_package(db_session):
    """Create a test package"""
    package = Package(
        name="Test Package",
        description="Test package description",
        price=99.99,
        interval="3 months",
        trial_days=30,
        max_projects=10,
        features=["Feature 1", "Feature 2"],
        button_text="Get Test Package",
        is_active=True,
        sort_order=1
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)
    
    yield package
    
    # Cleanup after test
    db_session.query(Package).filter(Package.id == package.id).delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_subscription(db_session, test_user, test_package):
    """Create a test subscription"""
    subscription = Subscription(
        user_id=test_user.id,
        package_id=test_package.id,
        mollie_id="sub_test",
        customer_id="cust_test",
        status="active",
        amount=test_package.price,
        interval=test_package.interval,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=90)
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    
    yield subscription
    
    # Cleanup after test
    db_session.query(Subscription).filter(Subscription.id == subscription.id).delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_invoice(db_session, test_user, test_subscription):
    """Create a test invoice"""
    from app.models.invoice import Invoice
    import os
    
    # Clean up any existing test invoices
    db_session.query(Invoice).filter(
        Invoice.user_id == test_user.id
    ).delete()
    db_session.commit()
    
    # Create test PDF file
    test_pdf_dir = "/tmp/test_invoices"
    os.makedirs(test_pdf_dir, exist_ok=True)
    test_pdf_path = os.path.join(test_pdf_dir, f"invoice_{int(datetime.now().timestamp())}.pdf")
    
    # Create empty PDF file
    with open(test_pdf_path, "wb") as f:
        f.write(b"Test PDF content")
    
    invoice = Invoice(
        invoice_number=f"INV-{datetime.now().strftime('%Y-%m')}-{str(test_user.id).zfill(4)}",
        user_id=test_user.id,
        subscription_id=test_subscription.id,
        issue_date=datetime.utcnow(),
        total_amount=test_subscription.amount,
        net_amount=test_subscription.amount / 1.19,  # Assuming 19% VAT
        vat_amount=test_subscription.amount - (test_subscription.amount / 1.19),
        vat_rate=0.19,
        pdf_path=test_pdf_path,
        status="paid",
        currency="EUR"
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    
    yield invoice
    
    # Cleanup after test
    db_session.query(Invoice).filter(
        Invoice.id == invoice.id
    ).delete()
    db_session.commit()
    
    # Clean up test PDF file
    if os.path.exists(test_pdf_path):
        os.remove(test_pdf_path)
