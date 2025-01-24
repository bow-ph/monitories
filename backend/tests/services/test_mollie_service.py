import pytest
from unittest.mock import patch, MagicMock
from app.services.mollie_service import MollieService
from mollie.api.error import Error as MollieError
from fastapi import HTTPException

@pytest.fixture
def mollie_service(db_session):
    with patch.dict('os.environ', {
        'MOLLIE_TEST_API_KEY': 'test_key',
        'MOLLIE_MODE': 'test'
    }):
        return MollieService(db_session)

@pytest.mark.asyncio
async def test_create_subscription(mollie_service):
    """Test creating a subscription"""
    mock_response = {
        "id": "sub_test",
        "customerId": "cust_test",
        "mode": "test",
        "status": "active",
        "amount": {"currency": "EUR", "value": "99.99"},
        "times": None,
        "interval": "3 months",
        "description": "Test Subscription",
        "webhookUrl": "https://example.com/webhook"
    }
    
    with patch.object(mollie_service.client.customers.subscriptions, 'with_parent_id') as mock_with_parent:
        mock_create = MagicMock()
        mock_create.create.return_value = mock_response
        mock_with_parent.return_value = mock_create
        
        result = await mollie_service.create_subscription(
            "cust_test",
            99.99,
            "3 months",
            "Test Subscription",
            "https://example.com/webhook"
        )
        
        assert result["id"] == "sub_test"
        assert result["status"] == "active"
        assert result["interval"] == "3 months"
        mock_with_parent.assert_called_once_with("cust_test")

@pytest.mark.asyncio
async def test_create_customer(mollie_service):
    """Test creating a customer"""
    mock_response = {
        "id": "cust_test",
        "mode": "test",
        "name": "Test Customer",
        "email": "test@example.com",
        "metadata": {"user_id": "123"}
    }
    
    with patch.object(mollie_service.client.customers, 'create') as mock_create:
        mock_create.return_value = mock_response
        
        result = await mollie_service.create_customer(
            "Test Customer",
            "test@example.com",
            {"user_id": "123"}
        )
        
        assert result["id"] == "cust_test"
        assert result["name"] == "Test Customer"
        assert result["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_handle_webhook_paid(mollie_service):
    """Test webhook handling for successful payment"""
    mock_payment = MagicMock()
    mock_payment.is_paid.return_value = True
    mock_payment.is_failed.return_value = False
    mock_payment.status = "paid"
    mock_payment.amount = {"currency": "EUR", "value": "99.99"}
    mock_payment.customer_id = "cust_test"
    mock_payment.subscription_id = "sub_test"
    mock_payment.metadata = {
        "package_name": "Team Package",
        "email": "test@example.com"
    }
    
    with patch.object(mollie_service.client.payments, 'get', return_value=mock_payment):
        result = await mollie_service.handle_webhook("tr_test")
        
        assert result["status"] == "paid"
        assert result["customer_id"] == "cust_test"
        assert result["subscription_id"] == "sub_test"

@pytest.mark.asyncio
async def test_handle_webhook_failed(mollie_service):
    """Test webhook handling for failed payment"""
    mock_payment = MagicMock()
    mock_payment.is_paid.return_value = False
    mock_payment.is_failed.return_value = True
    mock_payment.status = "failed"
    mock_payment.customer_id = "cust_test"
    mock_payment.subscription_id = "sub_test"
    mock_payment.metadata = {}
    
    with patch.object(mollie_service.client.payments, 'get', return_value=mock_payment):
        result = await mollie_service.handle_webhook("tr_test")
        
        assert result["status"] == "failed"
        assert result["customer_id"] == "cust_test"

@pytest.mark.asyncio
async def test_cancel_subscription(mollie_service):
    """Test canceling a subscription"""
    mock_response = {
        "id": "sub_test",
        "status": "canceled",
        "customerId": "cust_test"
    }
    
    with patch.object(mollie_service.client.customers.subscriptions, 'with_parent_id') as mock_with_parent:
        mock_delete = MagicMock()
        mock_delete.delete.return_value = mock_response
        mock_with_parent.return_value = mock_delete
        
        result = await mollie_service.cancel_subscription("cust_test", "sub_test")
        assert result["status"] == "canceled"
        mock_with_parent.assert_called_once_with("cust_test")
        mock_delete.delete.assert_called_once_with("sub_test")

@pytest.mark.asyncio
async def test_mollie_error_handling(mollie_service):
    """Test error handling for Mollie API errors"""
    with patch.object(mollie_service.client.customers, 'create', side_effect=MollieError("Test error")):
        with pytest.raises(HTTPException) as exc_info:
            await mollie_service.create_customer("Test", "test@example.com")
        assert exc_info.value.status_code == 400
        assert "Test error" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_list_subscriptions(mollie_service):
    """Test listing customer subscriptions"""
    mock_response = {
        "count": 1,
        "subscriptions": [{
            "id": "sub_test",
            "customerId": "cust_test",
            "status": "active"
        }]
    }
    
    with patch.object(mollie_service.client.customers.subscriptions, 'with_parent_id') as mock_with_parent:
        mock_list = MagicMock()
        mock_list.list.return_value = mock_response
        mock_with_parent.return_value = mock_list
        
        result = await mollie_service.list_subscriptions("cust_test")
        assert result["count"] == 1
        assert result["subscriptions"][0]["status"] == "active"
        mock_with_parent.assert_called_once_with("cust_test")
        mock_list.list.assert_called_once()
