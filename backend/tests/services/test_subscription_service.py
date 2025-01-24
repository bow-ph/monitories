import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app.services.subscription_service import SubscriptionService
from app.models.subscription import Subscription
from app.models.project import Project

@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def subscription_service(db_session):
    return SubscriptionService(db_session)

def test_trial_package_limits(subscription_service, db_session):
    """Test that trial package is limited to 1 project for 3 months"""
    # Mock current subscription
    mock_subscription = MagicMock()
    mock_subscription.package_type = "trial"
    mock_subscription.start_date = datetime.now()
    mock_subscription.end_date = datetime.now() + timedelta(days=90)
    
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    # Mock existing projects
    db_session.query(Project).filter().count.return_value = 0
    
    # Should allow creating first project
    assert subscription_service.can_create_project(user_id=1) is True
    
    # Mock one existing project
    db_session.query(Project).filter().count.return_value = 1
    
    # Should not allow creating second project
    assert subscription_service.can_create_project(user_id=1) is False

def test_team_package_limits(subscription_service, db_session):
    """Test that team package is limited to 10 projects per 3 months"""
    mock_subscription = MagicMock()
    mock_subscription.package_type = "team"
    mock_subscription.start_date = datetime.now()
    mock_subscription.end_date = datetime.now() + timedelta(days=90)
    
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    # Test with different project counts
    for i in range(11):
        db_session.query(Project).filter().count.return_value = i
        assert subscription_service.can_create_project(user_id=1) == (i < 10)

def test_enterprise_package_limits(subscription_service, db_session):
    """Test that enterprise package has custom limits"""
    current_time = datetime.now()
    mock_subscription = MagicMock()
    mock_subscription.package_type = "enterprise"
    mock_subscription.start_date = current_time
    mock_subscription.end_date = current_time + timedelta(days=365)
    mock_subscription.project_limit = 50  # Custom limit
    
    # Mock datetime.now() to return a fixed time
    with patch('app.services.subscription_service.datetime') as mock_datetime:
        mock_datetime.now.return_value = current_time
        db_session.query(Subscription).filter().first.return_value = mock_subscription
        
        # Test with different project counts
        for i in range(51):
            db_session.query(Project).filter().count.return_value = i
            assert subscription_service.can_create_project(user_id=1) == (i < 50)
    
    # Test with different project counts
    for i in range(51):
        db_session.query(Project).filter().count.return_value = i
        assert subscription_service.can_create_project(user_id=1) == (i < 50)

def test_subscription_expiry(subscription_service, db_session):
    """Test that expired subscriptions cannot create projects"""
    mock_subscription = MagicMock()
    mock_subscription.package_type = "team"
    mock_subscription.start_date = datetime.now() - timedelta(days=91)
    mock_subscription.end_date = datetime.now() - timedelta(days=1)
    
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    # Should not allow creating projects with expired subscription
    assert subscription_service.can_create_project(user_id=1) is False

def test_no_active_subscription(subscription_service, db_session):
    """Test that users without active subscription cannot create projects"""
    db_session.query(Subscription).filter().first.return_value = None
    assert subscription_service.can_create_project(user_id=1) is False

def test_subscription_duration(subscription_service):
    """Test subscription duration calculations"""
    # Trial package should be 3 months
    trial_duration = subscription_service.get_package_duration("trial")
    assert trial_duration == timedelta(days=90)
    
    # Team package should be 3 months
    team_duration = subscription_service.get_package_duration("team")
    assert team_duration == timedelta(days=90)
    
    # Enterprise package duration should be configurable
    enterprise_duration = subscription_service.get_package_duration("enterprise", custom_months=12)
    assert enterprise_duration == timedelta(days=365)
