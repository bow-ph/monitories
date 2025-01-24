from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.core.auth import get_current_user
from app.services.caldav_service import CalDAVService

router = APIRouter()

@router.get("/list", response_model=dict)
async def get_todo_list(
    status: Optional[str] = Query(None, enum=['pending', 'in_progress', 'completed']),
    priority: Optional[str] = Query(None, enum=['high', 'medium', 'low']),
    project_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get filtered todo list for current user"""
    try:
        # Base query for user's tasks
        query = db.query(Task).join(Task.project).filter(
            Project.user_id == current_user.id
        )
        
        # Apply filters
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if start_date:
            query = query.filter(Task.created_at >= start_date)
        if end_date:
            query = query.filter(Task.created_at <= end_date)
            
        # Get tasks
        tasks = query.all()
        
        # Count by status
        pending = sum(1 for task in tasks if task.status == 'pending')
        in_progress = sum(1 for task in tasks if task.status == 'in_progress')
        completed = sum(1 for task in tasks if task.status == 'completed')
        
        return {
            "items": [
                {
                    "id": task.id,
                    "description": task.description,
                    "estimated_hours": task.estimated_hours,
                    "actual_hours": task.actual_hours,
                    "status": task.status,
                    "priority": task.priority,
                    "confidence_score": task.confidence_score,
                    "confidence_rationale": task.confidence_rationale,
                    "project_id": task.project_id,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
                for task in tasks
            ],
            "total_items": len(tasks),
            "pending_items": pending,
            "in_progress_items": in_progress,
            "completed_items": completed
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get todo list: {str(e)}"
        )

@router.put("/tasks/{task_id}", response_model=dict)
async def update_todo_item(
    task_id: int,
    status: Optional[str] = Query(None, enum=['pending', 'in_progress', 'completed']),
    priority: Optional[str] = Query(None, enum=['high', 'medium', 'low']),
    actual_hours: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a todo item and sync with calendar"""
    try:
        # Get task
        task = db.query(Task).join(Task.project).filter(
            Task.id == task_id,
            Project.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        # Update task
        if status:
            task.status = status
        if priority:
            task.priority = priority
        if actual_hours is not None:
            task.actual_hours = actual_hours
            
        db.commit()
        
        try:
            # Sync with calendar
            caldav_service = CalDAVService()
            calendar_path = f"{current_user.id}/PM Tool"
            
            # Ensure calendar exists
            try:
                caldav_service.create_calendar(current_user.id)
            except Exception:
                pass  # Calendar might already exist
            
            # Prepare task data for sync
            task_data = {
                "id": task.id,
                "description": task.description,
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(hours=task.estimated_hours),
                "estimated_hours": task.estimated_hours,
                "status": task.status,
                "priority": task.priority,
                "confidence_score": task.confidence_score,
                "confidence_rationale": task.confidence_rationale
            }
            
            event_uid = caldav_service.sync_task_with_calendar(task_data, calendar_path)
            
            return {
                "status": "success",
                "task_id": task.id,
                "caldav_sync": {
                    "status": "synced",
                    "event_uid": event_uid
                }
            }
        except Exception as e:
            return {
                "status": "success",
                "task_id": task.id,
                "caldav_sync": {
                    "status": "failed",
                    "error": str(e)
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update task: {str(e)}"
        )

@router.get("/sync-status", response_model=dict)
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CalDAV synchronization status for user's tasks"""
    try:
        caldav_service = CalDAVService()
        calendar_path = f"{current_user.id}/PM Tool"
        
        # Get all user's tasks
        tasks = db.query(Task).join(Task.project).filter(
            Project.user_id == current_user.id
        ).all()
        
        # Check sync status for each task
        synced_count = 0
        failed_count = 0
        failed_tasks = []
        
        for task in tasks:
            try:
                event = caldav_service.find_task_event(calendar_path, task.id)
                if event:
                    synced_count += 1
                else:
                    failed_count += 1
                    failed_tasks.append(task.id)
            except Exception:
                failed_count += 1
                failed_tasks.append(task.id)
                
        return {
            "status": "success",
            "total_tasks": len(tasks),
            "synced_tasks": synced_count,
            "failed_tasks": failed_count,
            "failed_task_ids": failed_tasks,
            "last_sync": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )
