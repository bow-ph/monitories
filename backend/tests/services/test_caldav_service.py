import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from app.services.caldav_service import CalDAVService
from datetime import datetime, timedelta

@pytest.fixture
def caldav_service(monkeypatch):
    """Configure CalDAV test settings"""
    monkeypatch.setenv('TESTING', 'true')
    monkeypatch.setattr('app.core.config.settings.CALDAV_SERVER_URL', 'http://localhost:5232')
    monkeypatch.setattr('app.core.config.settings.CALDAV_AUTH_ENABLED', False)
    monkeypatch.setattr('app.core.config.settings.CALDAV_USERNAME', 'test_user')
    monkeypatch.setattr('app.core.config.settings.CALDAV_PASSWORD', 'test_pass')
    
    # Create service which will automatically use test mode with mocks
    service = CalDAVService()
    
    # Set up mock event for get_item
    mock_event = MagicMock()
    mock_event_data = {
        "uid": "test-uid",
        "summary": "Test Task",
        "dtstart": datetime.now().strftime("%Y%m%dT%H%M%SZ"),
        "dtend": (datetime.now() + timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ"),
        "description": "Estimated hours: 2.0",
        "x-pm-tool-estimated-hours": "2.0",
        "x-pm-tool-confidence": "0.8",
        "x-pm-tool-rationale": "Test rationale"
    }
    mock_event.get_component.return_value = mock_event_data
    service.storage.discover().get_item.return_value = mock_event
    
    # Configure mock collection methods
    service.storage.discover().list.return_value = [mock_event]
    
    return service

def test_calendar_path_format(caldav_service):
    """Test that calendar path follows the required format"""
    user_id = 123
    calendar_name = "Test Calendar"
    calendar_path = caldav_service.create_calendar(user_id, calendar_name)
    assert calendar_path == f"{user_id}/{calendar_name}"

@pytest.mark.asyncio
async def test_add_task(caldav_service):
    """Test adding a task to the calendar"""
    calendar_path = "123/Test Calendar"
    task_data = {
        "description": "Test Task",
        "start_date": datetime.now(),
        "end_date": datetime.now() + timedelta(hours=2),
        "estimated_hours": 2.0
    }
    
    mock_collection = MagicMock()
    mock_collection.upload = MagicMock()
    caldav_service.storage.discover.return_value = mock_collection
    
    event_uid = caldav_service.add_task(calendar_path, task_data)
    assert event_uid is not None
    assert mock_collection.upload.call_count == 1

@pytest.mark.asyncio
async def test_update_task(caldav_service):
    """Test updating an existing task"""
    calendar_path = "123/Test Calendar"
    event_uid = "test-uid"
    task_data = {
        "description": "Updated Task",
        "start_date": datetime.now(),
        "end_date": datetime.now() + timedelta(hours=2),
        "estimated_hours": 3.0
    }
    
    result = caldav_service.update_task(calendar_path, event_uid, task_data)
    assert result is True
    assert caldav_service.storage.discover().upload.call_count == 1

@pytest.mark.asyncio
async def test_delete_task(caldav_service):
    """Test deleting a task"""
    calendar_path = "123/Test Calendar"
    event_uid = "test-uid"
    
    result = caldav_service.delete_task(calendar_path, event_uid)
    assert result is True
    assert caldav_service.storage.discover().delete.call_count == 1

@pytest.mark.asyncio
async def test_get_tasks(caldav_service):
    """Test retrieving tasks in a date range"""
    calendar_path = "123/Test Calendar"
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    mock_event_data = {
        "uid": "test-uid",
        "summary": "Test Task",
        "dtstart": start_date.strftime("%Y%m%dT%H%M%SZ"),
        "dtend": (start_date + timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ"),
        "description": "Estimated hours: 2.0",
        "x-pm-tool-estimated-hours": "2.0",
        "x-pm-tool-confidence": "0.8",
        "x-pm-tool-rationale": "Test rationale"
    }
    
    tasks = caldav_service.get_tasks(calendar_path, start_date, end_date)
    assert len(tasks) == 1
    assert tasks[0]["uid"] == "test-uid"
    assert tasks[0]["estimated_hours"] == 2.0

def test_authentication_disabled(monkeypatch):
    """Test CalDAV service with authentication disabled"""
    monkeypatch.setenv('TESTING', 'true')
    monkeypatch.setattr('app.core.config.settings.CALDAV_AUTH_ENABLED', False)
    
    service = CalDAVService()
    assert service.storage.configuration["auth"]["type"] == "none"
    assert not service.storage.configuration.get("htpasswd_filename")

def test_authentication_enabled(monkeypatch):
    """Test CalDAV service with authentication enabled"""
    monkeypatch.setenv('TESTING', 'true')
    monkeypatch.setattr('app.core.config.settings.CALDAV_AUTH_ENABLED', True)
    monkeypatch.setattr('app.core.config.settings.CALDAV_USERNAME', 'test_user')
    monkeypatch.setattr('app.core.config.settings.CALDAV_PASSWORD', 'test_pass')
    
    service = CalDAVService()
    assert service.storage.configuration["auth"]["type"] == "htpasswd"
    assert service.storage.configuration["auth"]["htpasswd_encryption"] == "bcrypt"
