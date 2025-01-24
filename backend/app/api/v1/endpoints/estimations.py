from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List

from app.core.database import get_db
from app.models.user import User
from app.core.auth import get_current_user
from app.services.estimation_service import EstimationService

router = APIRouter()

@router.get("/tasks/{task_id}/accuracy")
def analyze_task_estimate(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Analyze the accuracy of a task's time estimate"""
    try:
        estimation_service = EstimationService(db)
        return estimation_service.analyze_estimate_accuracy(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/stats")
def get_project_estimation_stats(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get estimation statistics for an entire project"""
    try:
        estimation_service = EstimationService(db)
        return estimation_service.get_project_estimation_stats(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/me/estimation-patterns")
def get_user_estimation_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Detect patterns in estimation accuracy across all user projects"""
    try:
        estimation_service = EstimationService(db)
        return estimation_service.detect_estimation_patterns(current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
