from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime

from app.core.database import get_db
from app.services.scheduling_service import SchedulingService
from app.models.project import Project

router = APIRouter()

@router.post("/projects/{project_id}/schedule", response_model=Dict)
async def schedule_project(
    project_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Create an optimal schedule for project tasks
    """
    try:
        scheduling_service = SchedulingService(db)
        schedule = scheduling_service.schedule_tasks(project_id)
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling project: {str(e)}")

@router.get("/projects/{project_id}/available-slots", response_model=List[Dict])
async def get_available_slots(
    project_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get available time slots for scheduling between two dates
    """
    try:
        scheduling_service = SchedulingService(db)
        slots = scheduling_service.get_available_slots(start_date, end_date)
        return slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting available slots: {str(e)}")

@router.post("/projects/{project_id}/validate-schedule", response_model=Dict)
async def validate_schedule(
    project_id: int,
    schedule: List[Dict],
    db: Session = Depends(get_db)
) -> Dict:
    """
    Validate a proposed schedule for conflicts and constraints
    """
    try:
        scheduling_service = SchedulingService(db)
        validation_result = scheduling_service.validate_schedule(schedule)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating schedule: {str(e)}")
