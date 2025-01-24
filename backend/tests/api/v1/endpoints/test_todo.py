import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from app.models.task import Task
from app.models.project import Project
from app.models.user import User

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        is_active=True,
        hashed_password="test_hash",
        client_type="private"
    )

@pytest.fixture
def auth_headers(mock_user):
    from app.core.auth import create_access_token
    access_token = create_access_token(data={"sub": mock_user.email})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def mock_project():
    return Project(
        id=1,
        user_id=1,
        name="Test Project",
        description="Test project description"
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
        priority="medium",
        confidence_score=0.8,
        confidence_rationale="Test rationale"
    )

def test_get_todo_list(client, mock_task, test_user, db_session):
    """Test getting todo list with filters"""
    # Create project for test user
    project = Project(
        user_id=test_user.id,
        name="Test Project",
        description="Test project description"
    )
    db_session.add(project)
    db_session.commit()
    
    # Create task for project
    task = Task(
        project_id=project.id,
        description=mock_task.description,
        estimated_hours=mock_task.estimated_hours,
        status=mock_task.status,
        priority=mock_task.priority,
        confidence_score=mock_task.confidence_score,
        confidence_rationale=mock_task.confidence_rationale
    )
    db_session.add(task)
    db_session.commit()
    
    response = client.get("/api/v1/todo/list")
    assert response.status_code == 200
    result = response.json()
    assert result["total_items"] == 1
    assert result["pending_items"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["description"] == task.description

def test_get_todo_list_with_filters(client, mock_task, test_user, db_session):
    """Test todo list with status and priority filters"""
    # Create project for test user
    project = Project(
        user_id=test_user.id,
        name="Test Project",
        description="Test project description"
    )
    db_session.add(project)
    db_session.commit()
    
    # Create task for project
    task = Task(
        project_id=project.id,
        description=mock_task.description,
        estimated_hours=mock_task.estimated_hours,
        status="pending",
        priority="medium",
        confidence_score=mock_task.confidence_score,
        confidence_rationale=mock_task.confidence_rationale
    )
    db_session.add(task)
    db_session.commit()
    
    response = client.get("/api/v1/todo/list?status=pending&priority=medium")
    assert response.status_code == 200
    result = response.json()
    assert result["total_items"] == 1
    assert result["items"][0]["status"] == "pending"
    assert result["items"][0]["priority"] == "medium"

def test_update_todo_item(client, mock_task, test_user, db_session):
    """Test updating todo item status and priority"""
    # Create project for test user
    project = Project(
        user_id=test_user.id,
        name="Test Project",
        description="Test project description"
    )
    db_session.add(project)
    db_session.commit()
    
    # Create task for project
    task = Task(
        project_id=project.id,
        description=mock_task.description,
        estimated_hours=mock_task.estimated_hours,
        status="pending",
        priority="medium",
        confidence_score=mock_task.confidence_score,
        confidence_rationale=mock_task.confidence_rationale
    )
    db_session.add(task)
    db_session.commit()
    
    with patch('app.api.v1.endpoints.todo.CalDAVService') as mock_caldav:
        # Mock CalDAV service
        mock_caldav.return_value.sync_task_with_calendar.return_value = "test-uid"
        
        response = client.put(
            f"/api/v1/todo/tasks/{task.id}?status=completed&priority=high"
        )
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["caldav_sync"]["status"] == "synced"

def test_update_nonexistent_task(client):
    """Test updating a task that doesn't exist"""
    with patch('app.api.v1.endpoints.todo.get_db', return_value=MagicMock()) as mock_db:
        # Mock database queries
        mock_db.return_value.query.return_value.join.return_value.filter.return_value.first.return_value = None
        
        response = client.put("/api/v1/todo/tasks/999?status=completed")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

def test_get_sync_status(client, mock_task, test_user, db_session):
    """Test getting CalDAV sync status"""
    # Create project for test user
    project = Project(
        user_id=test_user.id,
        name="Test Project",
        description="Test project description"
    )
    db_session.add(project)
    db_session.commit()
    
    # Create task for project
    task = Task(
        project_id=project.id,
        description=mock_task.description,
        estimated_hours=mock_task.estimated_hours,
        status="pending",
        priority="medium",
        confidence_score=mock_task.confidence_score,
        confidence_rationale=mock_task.confidence_rationale
    )
    db_session.add(task)
    db_session.commit()
    
    with patch('app.api.v1.endpoints.todo.CalDAVService') as mock_caldav:
        # Mock CalDAV service
        mock_caldav.return_value.find_task_event.return_value = True
        
        response = client.get("/api/v1/todo/sync-status")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["total_tasks"] == 1
        assert result["synced_tasks"] == 1
        assert result["failed_tasks"] == 0
