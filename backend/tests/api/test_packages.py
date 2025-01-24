import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.package import Package
from app.models.user import User

client = TestClient(app)

# Using test_package fixture from conftest.py

def test_list_packages(client, db_session, test_package):
    """Test listing all active packages"""
    response = client.get("/api/v1/packages")
    assert response.status_code == 200
    packages = response.json()
    assert len(packages) >= 1
    assert packages[0]["name"] == test_package.name
    assert packages[0]["price"] == test_package.price

def test_create_package_unauthorized(client, db_session):
    """Test that non-admin users cannot create packages"""
    package_data = {
        "name": "New Package",
        "description": "New Description",
        "price": 149.99,
        "interval": "3 months",
        "max_projects": 15,
        "features": ["Feature 1", "Feature 2"],
        "button_text": "Get Started"
    }
    
    # With non-admin user token
    headers = {"Authorization": "Bearer test_token"}
    with patch('app.core.auth.get_current_user') as mock_auth:
        mock_auth.return_value = User(id=1, email="test@example.com", is_superuser=False)
        response = client.post("/api/v1/packages/", json=package_data, headers=headers)
        assert response.status_code == 403

def test_create_package_authorized(client, db_session):
    """Test package creation by admin"""
    package_data = {
        "name": "New Package",
        "description": "New Description",
        "price": 149.99,
        "interval": "3 months",
        "max_projects": 15,
        "features": ["Feature 1", "Feature 2"],
        "button_text": "Get Started"
    }
    headers = {"Authorization": "Bearer test_token"}
    with patch('app.core.auth.get_current_user') as mock_auth:
        mock_auth.return_value = User(id=1, email="test@example.com", is_superuser=True)
        response = client.post("/api/v1/packages/", json=package_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == package_data["name"]
        assert data["price"] == package_data["price"]
        assert data["interval"] == package_data["interval"]
        assert data["max_projects"] == package_data["max_projects"]
        assert data["interval"] == package_data["interval"]
        assert data["max_projects"] == package_data["max_projects"]
        assert data["features"] == package_data["features"]
        assert data["button_text"] == package_data["button_text"]

def test_update_package(db_session, test_package):
    """Test updating a package"""
    update_data = {
        "price": 199.99,
        "description": "Updated Description"
    }
    headers = {"Authorization": "Bearer test_token"}
    with patch('app.core.auth.get_current_user') as mock_auth:
        mock_auth.return_value = User(id=1, email="test@example.com", is_superuser=True)
        response = client.put(
            f"/api/v1/packages/{test_package.id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == update_data["price"]
        assert data["description"] == update_data["description"]

def test_delete_package(db_session, test_package):
    """Test soft deleting a package"""
    headers = {"Authorization": "Bearer test_token"}
    with patch('app.core.auth.get_current_user') as mock_auth:
        mock_auth.return_value = User(id=1, email="test@example.com", is_superuser=True)
        response = client.delete(
            f"/api/v1/packages/{test_package.id}",
            headers=headers
        )
        assert response.status_code == 200
        
        # Verify package is not returned in list
        response = client.get("/api/v1/packages")
        packages = response.json()
        assert not any(p["id"] == test_package.id for p in packages)
