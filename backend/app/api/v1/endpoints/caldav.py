from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import re
import uuid

from app.core.database import get_db
from app.models.user import User
from app.core.auth import get_current_user
from app.core.config import settings
from app.services.caldav_service import CalDAVService

# Pydantic models for request/response
class TaskData(BaseModel):
    description: str
    start_date: datetime
    end_date: datetime
    estimated_hours: float

class CalendarResponse(BaseModel):
    calendar_path: str
    caldav_url: str

class TaskResponse(BaseModel):
    event_uid: str
    caldav_url: str

def validate_calendar_path(path: str) -> bool:
    """Validate calendar path format (user_id/calendar_name)"""
    pattern = r'^\d+/[^/]+$'
    return bool(re.match(pattern, path))

router = APIRouter()

@router.post("/calendars", response_model=CalendarResponse)
def create_calendar(
    calendar_name: str = Path(..., description="Name of the calendar to create"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar for the current user"""
    try:
        caldav_service = CalDAVService()
        calendar_path = caldav_service.create_calendar(current_user.id, calendar_name)
        caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
        return CalendarResponse(calendar_path=calendar_path, caldav_url=caldav_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create calendar: {str(e)}"
        )

@router.post("/tasks/{calendar_path}", response_model=TaskResponse)
def add_task(
    task_data: TaskData,
    calendar_path: str = Path(..., description="Calendar path in format: user_id/calendar_name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a task to the calendar"""
    if not validate_calendar_path(calendar_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid calendar path. Must be in format: user_id/calendar_name"
        )
    
    try:
        caldav_service = CalDAVService()
        event_uid = caldav_service.add_task(calendar_path, task_data.dict())
        caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
        return TaskResponse(event_uid=event_uid, caldav_url=caldav_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add task: {str(e)}"
        )

@router.put("/tasks/{calendar_path}/{event_uid}", response_model=TaskResponse)
def update_task(
    task_data: TaskData,
    calendar_path: str = Path(..., description="Calendar path in format: user_id/calendar_name"),
    event_uid: str = Path(..., description="Unique identifier of the event to update"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing task in the calendar"""
    if not validate_calendar_path(calendar_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid calendar path. Must be in format: user_id/calendar_name"
        )
    
    try:
        caldav_service = CalDAVService()
        if caldav_service.update_task(calendar_path, event_uid, task_data.dict()):
            caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
            return TaskResponse(event_uid=event_uid, caldav_url=caldav_url)
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update task: {str(e)}"
        )

class TaskList(BaseModel):
    tasks: List[TaskData]
    caldav_url: str

class DeleteResponse(BaseModel):
    status: str
    caldav_url: str

@router.delete("/tasks/{calendar_path}/{event_uid}", response_model=DeleteResponse)
def delete_task(
    calendar_path: str = Path(..., description="Calendar path in format: user_id/calendar_name"),
    event_uid: str = Path(..., description="Unique identifier of the event to delete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task from the calendar"""
    if not validate_calendar_path(calendar_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid calendar path. Must be in format: user_id/calendar_name"
        )
    
    try:
        caldav_service = CalDAVService()
        if caldav_service.delete_task(calendar_path, event_uid):
            caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
            return DeleteResponse(status="deleted", caldav_url=caldav_url)
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete task: {str(e)}"
        )

@router.get("/tasks/{calendar_path}", response_model=TaskList)
def get_tasks(
    calendar_path: str = Path(..., description="Calendar path in format: user_id/calendar_name"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks from the calendar with optional date filtering"""
    if not validate_calendar_path(calendar_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid calendar path. Must be in format: user_id/calendar_name"
        )
    
    try:
        caldav_service = CalDAVService()
        tasks = caldav_service.get_tasks(calendar_path, start_date, end_date)
        caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
        return TaskList(tasks=tasks, caldav_url=caldav_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tasks: {str(e)}"
        )
