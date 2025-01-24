import pytest
from app.models.user import User
from app.core.auth import create_access_token

def test_get_all_users_unauthorized(client, test_user, db_session):
    """Test that non-admin users cannot access the admin endpoints"""
    # Create access token for regular user
    access_token = create_access_token({"sub": test_user.email})
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403

def test_get_all_users_authorized(client, db_session, admin_user):
    """Test that admin users can access the user list"""
    # Create some test users
    users = [
        User(
            email=f"test{i}@example.com",
            hashed_password="test",
            is_active=True,
            client_type="private"
        )
        for i in range(3)
    ]
    for user in users:
        db_session.add(user)
    db_session.commit()

    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # At least our test users

def test_get_user_details(client, db_session, admin_user, test_user):
    """Test getting details of a specific user"""
    response = client.get(
        f"/api/v1/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["client_type"] == test_user.client_type

def test_update_user_details(client, db_session, admin_user, test_user):
    """Test updating user details including client information"""
    update_data = {
        "client_type": "company",
        "company_name": "Updated Corp",
        "vat_number": "DE987654321",
        "billing_address": "Test Street 123\n12345 Test City",
        "shipping_address": "Ship Street 456\n67890 Ship City",
        "contact_person": "John Doe",
        "phone_number": "+49123456789",
        "notes": "Important client",
        "is_active": True
    }
    
    response = client.put(
        f"/api/v1/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_user['token']}"},
        json=update_data
    )
    assert response.status_code == 200
    result = response.json()
    
    # Verify response contains updated data
    for key, value in update_data.items():
        if key in result:  # Only check fields that are in the response
            assert result[key] == value
    
    # Verify the changes in database
    updated_user = db_session.query(User).filter(User.id == test_user.id).first()
    for key, value in update_data.items():
        assert getattr(updated_user, key) == value

def test_update_user_unauthorized(client, db_session, test_user):
    """Test that non-admin users cannot update user details"""
    # Create access token for regular user
    access_token = create_access_token({"sub": test_user.email})
    update_data = {
        "client_type": "company",
        "company_name": "Unauthorized Update"
    }
    
    response = client.put(
        f"/api/v1/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data
    )
    assert response.status_code == 403

def test_update_user_invalid_data(client, db_session, admin_user, test_user):
    """Test validation of user update data"""
    invalid_data = {
        "client_type": "invalid_type",  # Should be 'private' or 'company'
        "vat_number": "INVALID"  # Should start with DE for German VAT
    }
    
    response = client.put(
        f"/api/v1/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_user['token']}"},
        json=invalid_data
    )
    assert response.status_code == 400
    assert "detail" in response.json()
