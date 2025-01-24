import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.subscription import Subscription
from app.models.user import User
from datetime import datetime, timedelta

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        is_active=True
    )

@pytest.fixture
def mock_subscription():
    return Subscription(
        id=1,
        user_id=1,
        mollie_id="sub_test",
        customer_id="cust_test",
        package_id=1,
        package_type="team",
        project_limit=10,
        status="active",
        amount=119.0,
        interval="3 months",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=90)
    )

def test_get_my_subscription(mock_user, mock_subscription):
    """Test getting current user's subscription"""
    with patch('app.api.v1.endpoints.subscriptions.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.subscriptions.get_db'), \
         patch('app.services.subscription_service.SubscriptionService.get_user_subscription', return_value=mock_subscription):
        
        response = client.get("/v1/subscriptions/me")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == mock_subscription.id
        assert data["package_type"] == "team"
        assert data["status"] == "active"

def test_get_my_subscription_not_found(mock_user):
    """Test getting subscription when none exists"""
    with patch('app.api.v1.endpoints.subscriptions.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.subscriptions.get_db'), \
         patch('app.services.subscription_service.SubscriptionService.get_user_subscription', return_value=None):
        
        response = client.get("/v1/subscriptions/me")
        assert response.status_code == 404
        assert response.json()["detail"] == "No active subscription found"

def test_check_project_limit(mock_user):
    """Test checking project creation limit"""
    limit_response = {
        "can_create": True,
        "current_count": 5,
        "limit": 10,
        "reason": None
    }
    
    with patch('app.api.v1.endpoints.subscriptions.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.subscriptions.get_db'), \
         patch('app.services.subscription_service.SubscriptionService.can_create_project', return_value=limit_response):
        
        response = client.get("/v1/subscriptions/me/project-limit")
        assert response.status_code == 200
        data = response.json()
        assert data["can_create"] is True
        assert data["current_count"] == 5
        assert data["limit"] == 10

def test_cancel_subscription(mock_user, mock_subscription):
    """Test subscription cancellation"""
    cancel_response = {
        "status": "success",
        "message": "Subscription cancelled successfully",
        "end_date": (datetime.now() + timedelta(days=90)).isoformat()
    }
    
    with patch('app.api.v1.endpoints.subscriptions.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.subscriptions.get_db'), \
         patch('app.services.subscription_service.SubscriptionService.get_user_subscription', return_value=mock_subscription), \
         patch('app.services.subscription_service.SubscriptionService.cancel_subscription', return_value=cancel_response):
        
        response = client.post("/v1/subscriptions/me/cancel", json={"reason": "Test cancellation"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "end_date" in data

def test_cancel_subscription_not_found(mock_user):
    """Test cancellation when no subscription exists"""
    with patch('app.api.v1.endpoints.subscriptions.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.subscriptions.get_db'), \
         patch('app.services.subscription_service.SubscriptionService.get_user_subscription', return_value=None):
        
        response = client.post("/v1/subscriptions/me/cancel")
        assert response.status_code == 404
        assert response.json()["detail"] == "No active subscription found"
