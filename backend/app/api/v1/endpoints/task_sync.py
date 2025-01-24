from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.core.auth import get_current_user
from app.services.caldav_service import CalDAVService

router = APIRouter()

@router.post("/tasks/{task_id}/sync", response_model=dict)
async def sync_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Synchronize a task with the user's calendar"""
    try:
        # Get task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Create calendar path
        calendar_path = f"{current_user.id}/PM Tool"
        
        # Sync task
        caldav_service = CalDAVService()
        event_uid = caldav_service.sync_task_with_calendar(task, calendar_path)
        
        return {
            "status": "synced",
            "event_uid": event_uid,
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync task: {str(e)}"
        )

@router.post("/tasks/sync-all", response_model=dict)
async def sync_all_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Synchronize all user's tasks with their calendar"""
    try:
        # Get all user's tasks
        tasks = db.query(Task).join(Task.project).filter(
            Task.project.has(user_id=current_user.id)
        ).all()
        
        # Create calendar path
        calendar_path = f"{current_user.id}/PM Tool"
        
        # Sync each task
        caldav_service = CalDAVService()
        synced_tasks = []
        failed_tasks = []
        
        for task in tasks:
            try:
                event_uid = caldav_service.sync_task_with_calendar(task, calendar_path)
                synced_tasks.append({
                    "task_id": task.id,
                    "event_uid": event_uid
                })
            except Exception as e:
                failed_tasks.append({
                    "task_id": task.id,
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "synced_count": len(synced_tasks),
            "failed_count": len(failed_tasks),
            "synced_tasks": synced_tasks,
            "failed_tasks": failed_tasks
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync tasks: {str(e)}"
        )
