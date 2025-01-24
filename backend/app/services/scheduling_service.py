from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.project import Project
from app.services.openai_service import OpenAIService

class SchedulingService:
    """Service for handling task scheduling and timeline management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_service = OpenAIService()

    def schedule_tasks(self, project_id: int) -> Dict:
        """
        Create an optimal schedule for project tasks considering dependencies and constraints
        
        Args:
            project_id: The ID of the project to schedule
            
        Returns:
            Dict containing the scheduling plan with task timelines
        """
        # Get project and its tasks
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
            
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        if not tasks:
            return {
                "status": "error",
                "message": "No tasks found for project"
            }
            
        # Convert tasks to scheduling format
        task_data = [
            {
                "id": task.id,
                "description": task.description,
                "estimated_hours": task.estimated_hours,
                "confidence_score": task.confidence_score,
                "status": task.status
            }
            for task in tasks
        ]
        
        # Calculate working hours (8 hours per day, excluding weekends)
        schedule = self._create_schedule(task_data)
        
        return {
            "status": "success",
            "project_id": project_id,
            "schedule": schedule,
            "total_duration_days": len(schedule),
            "earliest_start": schedule[0]["date"] if schedule else None,
            "latest_end": schedule[-1]["date"] if schedule else None
        }
        
    def _create_schedule(self, tasks: List[Dict]) -> List[Dict]:
        """Create a daily schedule for tasks"""
        schedule = []
        current_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        remaining_hours = 8.0  # Standard work day
        
        for task in tasks:
            task_hours = task["estimated_hours"]
            
            while task_hours > 0:
                # Skip weekends
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    current_date = current_date.replace(hour=9, minute=0)
                    remaining_hours = 8.0
                    continue
                
                # Calculate hours to allocate in current day
                hours_today = min(remaining_hours, task_hours)
                
                # Add to schedule
                schedule.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "task_id": task["id"],
                    "description": task["description"],
                    "hours": hours_today,
                    "start_time": current_date.strftime("%H:%M"),
                    "end_time": (current_date + timedelta(hours=hours_today)).strftime("%H:%M")
                })
                
                task_hours -= hours_today
                remaining_hours -= hours_today
                
                # Move to next day if current day is full
                if remaining_hours <= 0:
                    current_date += timedelta(days=1)
                    current_date = current_date.replace(hour=9, minute=0)
                    remaining_hours = 8.0
                else:
                    current_date += timedelta(hours=hours_today)
                    
        return schedule

    def get_available_slots(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get available time slots between two dates"""
        slots = []
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Skip weekends
                slots.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "available_hours": 8.0,
                    "start_time": "09:00",
                    "end_time": "17:00"
                })
            current_date += timedelta(days=1)
            
        return slots

    def validate_schedule(self, schedule: List[Dict]) -> Dict:
        """Validate a schedule for conflicts and constraints"""
        validation = {
            "is_valid": True,
            "conflicts": [],
            "warnings": []
        }
        
        # Check for overbooked days
        daily_hours = {}
        for slot in schedule:
            date = slot["date"]
            hours = slot["hours"]
            
            if date not in daily_hours:
                daily_hours[date] = hours
            else:
                daily_hours[date] += hours
                
            if daily_hours[date] > 8:
                validation["is_valid"] = False
                validation["conflicts"].append(
                    f"Overbooked day on {date}: {daily_hours[date]} hours scheduled"
                )
                
        # Check for weekend work
        for slot in schedule:
            date_obj = datetime.strptime(slot["date"], "%Y-%m-%d")
            if date_obj.weekday() >= 5:
                validation["warnings"].append(
                    f"Weekend work scheduled on {slot['date']}"
                )
                
        return validation
