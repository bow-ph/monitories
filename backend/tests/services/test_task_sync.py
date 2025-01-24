import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from app.services.caldav_service import CalDAVService
from app.models.task import Task
from app.models.project import Project

@pytest.fixture
def mock_task():
    return Task(
        id=1,
        project_id=1,
        description="Test Task",
        estimated_hours=4.0,
        actual_hours=None,
        status="pending",
        confidence_score=0.8,
        confidence_rationale="Test rationale"
    )

@pytest.fixture
def mock_project():
    return Project(
        id=1,
        user_id=1,
        name="Test Project",
        description="Test project description",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )

@pytest.fixture
def caldav_service():
    """Create a CalDAV service instance with mocked storage"""
    with patch.dict('os.environ', {'TESTING': 'true'}):
        service = CalDAVService()
        return service

def test_sync_task_with_calendar_new_task(caldav_service, mock_task):
    """Test syncing a new task to calendar"""
    # Mock calendar discovery
    mock_collection = MagicMock()
    mock_collection.list.return_value = []
    caldav_service.storage.discover.return_value = mock_collection
    
    # Test sync
    event_uid = caldav_service.sync_task_with_calendar(mock_task, "1/Test Calendar")
    
    assert isinstance(event_uid, str)
    caldav_service.storage.discover.assert_called_once()
    mock_collection.list.assert_called_once()
    mock_collection.upload.assert_called_once()

def test_sync_task_with_calendar_existing_task(caldav_service, mock_task):
    """Test syncing an existing task"""
    # Mock existing event
    mock_event = MagicMock()
    mock_event.get_component.return_value = {
        "uid": "test-uid",
        "x-pm-tool-id": "1"
    }
    
    # Mock calendar discovery
    mock_collection = MagicMock()
    mock_collection.list.return_value = [mock_event]
    caldav_service.storage.discover.return_value = mock_collection
    
    # Test sync
    event_uid = caldav_service.sync_task_with_calendar(mock_task, "1/Test Calendar")
    
    assert event_uid == "test-uid"
    caldav_service.storage.discover.assert_called_once()
    mock_collection.list.assert_called_once()
    mock_collection.upload.assert_called_once()

def test_sync_task_with_calendar_validation(caldav_service, mock_task):
    """Test task validation during sync"""
    # Test with invalid task (no description)
    mock_task.description = None
    
    with pytest.raises(ValueError, match="Missing required fields"):
        caldav_service.sync_task_with_calendar(mock_task, "1/Test Calendar")
    
    # Test with invalid estimated hours
    mock_task.description = "Test Task"
    mock_task.estimated_hours = -1
    
    with pytest.raises(ValueError, match="estimated_hours must be positive"):
        caldav_service.sync_task_with_calendar(mock_task, "1/Test Calendar")

def test_sync_task_with_calendar_not_found(caldav_service, mock_task):
    """Test syncing when calendar not found"""
    # Mock calendar not found
    caldav_service.storage.discover.return_value = None
    
    with pytest.raises(ValueError, match="Calendar not found"):
        caldav_service.sync_task_with_calendar(mock_task, "1/Test Calendar")

def test_sync_task_with_calendar_error_handling(caldav_service, mock_task):
    """Test error handling during sync"""
    # Mock upload error
    mock_collection = MagicMock()
    mock_collection.list.return_value = []
    mock_collection.upload.side_effect = Exception("Upload failed")
    caldav_service.storage.discover.return_value = mock_collection
    
    with pytest.raises(ValueError, match="Failed to sync task"):
        caldav_service.sync_task_with_calendar(mock_task, "1/Test Calendar")
