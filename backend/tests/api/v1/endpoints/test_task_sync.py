import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.services.caldav_service import CalDAVService

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        is_active=True
    )

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

def test_sync_task_success(mock_user, mock_task, mock_project):
    """Test successful task synchronization"""
    with patch('app.api.v1.endpoints.task_sync.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.task_sync.get_db'), \
         patch('app.api.v1.endpoints.task_sync.CalDAVService') as mock_caldav:
        
        # Mock database queries
        db = MagicMock()
        db.query(Task).filter().first.return_value = mock_task
        
        # Mock CalDAV service
        mock_caldav.return_value.sync_task_with_calendar.return_value = "test-uid"
        
        response = client.post(f"/v1/task-sync/tasks/{mock_task.id}/sync")
        assert response.status_code == 200
        assert response.json() == {
            "status": "synced",
            "event_uid": "test-uid",
            "task_id": mock_task.id
        }

def test_sync_task_not_found(mock_user):
    """Test synchronization of non-existent task"""
    with patch('app.api.v1.endpoints.task_sync.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.task_sync.get_db'):
        
        # Mock database queries
        db = MagicMock()
        db.query(Task).filter().first.return_value = None
        
        response = client.post("/v1/task-sync/tasks/999/sync")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

def test_sync_all_tasks_success(mock_user, mock_task, mock_project):
    """Test successful synchronization of all tasks"""
    with patch('app.api.v1.endpoints.task_sync.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.task_sync.get_db'), \
         patch('app.api.v1.endpoints.task_sync.CalDAVService') as mock_caldav:
        
        # Mock database queries
        db = MagicMock()
        db.query(Task).join().filter().all.return_value = [mock_task]
        
        # Mock CalDAV service
        mock_caldav.return_value.sync_task_with_calendar.return_value = "test-uid"
        
        response = client.post("/v1/task-sync/tasks/sync-all")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "completed"
        assert result["synced_count"] == 1
        assert result["failed_count"] == 0
        assert len(result["synced_tasks"]) == 1
        assert result["synced_tasks"][0]["task_id"] == mock_task.id

def test_sync_all_tasks_partial_failure(mock_user, mock_task, mock_project):
    """Test synchronization with some tasks failing"""
    with patch('app.api.v1.endpoints.task_sync.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.task_sync.get_db'), \
         patch('app.api.v1.endpoints.task_sync.CalDAVService') as mock_caldav:
        
        # Mock database queries
        db = MagicMock()
        db.query(Task).join().filter().all.return_value = [mock_task, mock_task]
        
        # Mock CalDAV service to succeed for first task and fail for second
        mock_caldav.return_value.sync_task_with_calendar.side_effect = [
            "test-uid",
            ValueError("Sync failed")
        ]
        
        response = client.post("/v1/task-sync/tasks/sync-all")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "completed"
        assert result["synced_count"] == 1
        assert result["failed_count"] == 1
        assert len(result["synced_tasks"]) == 1
        assert len(result["failed_tasks"]) == 1

def test_sync_all_tasks_no_tasks(mock_user):
    """Test synchronization when user has no tasks"""
    with patch('app.api.v1.endpoints.task_sync.get_current_user', return_value=mock_user), \
         patch('app.api.v1.endpoints.task_sync.get_db'):
        
        # Mock database queries
        db = MagicMock()
        db.query(Task).join().filter().all.return_value = []
        
        response = client.post("/v1/task-sync/tasks/sync-all")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "completed"
        assert result["synced_count"] == 0
        assert result["failed_count"] == 0
        assert len(result["synced_tasks"]) == 0
