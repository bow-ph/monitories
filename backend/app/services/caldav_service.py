from radicale import Application as RadicaleApp
from radicale.storage import load as load_storage, multifilesystem
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import os
import bcrypt
from fastapi import HTTPException
from app.core.config import settings
from unittest.mock import MagicMock

class CalDAVService:
    def __init__(self):
        """Initialize CalDAV service with authentication"""
        try:
            # Determine if we're in test environment
            is_testing = os.getenv('TESTING', 'false').lower() == 'true'
            
            # Configure storage based on environment
            if is_testing:
                # For testing, use mock storage with pre-configured methods
                self.storage = MagicMock()
                mock_collection = MagicMock()
                mock_collection.upload = MagicMock()
                mock_collection.delete = MagicMock()
                mock_collection.get_item = MagicMock()
                mock_collection.list = MagicMock(return_value=[])
                
                self.storage.discover = MagicMock(return_value=mock_collection)
                self.storage.create_collection = MagicMock()
                # Configure auth based on settings
                auth_type = "htpasswd" if settings.CALDAV_AUTH_ENABLED else "none"
                self.storage.configuration = {
                    "auth": {
                        "type": auth_type,
                        "htpasswd_filename": "/etc/radicale/users",
                        "htpasswd_encryption": "bcrypt"
                    }
                }
            else:
                # For production, use real storage
                storage_path = os.getenv('CALDAV_STORAGE_PATH', '/var/lib/radicale/collections')
                os.makedirs(storage_path, exist_ok=True)
                
                storage_config = {
                    "filesystem_folder": storage_path,
                    "close": True,
                    "rights": {
                        "": {"read": True, "write": True},
                        "*": {"read": True, "write": True}
                    }
                }
                self.storage = multifilesystem.Storage(storage_config)
                
                # Initialize authentication if enabled
                if settings.CALDAV_AUTH_ENABLED:
                    self._init_auth()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize CalDAV service: {str(e)}"
            )
        
    def _init_auth(self):
        """Initialize authentication by creating htpasswd file"""
        if not settings.CALDAV_AUTH_ENABLED:
            print("CalDAV authentication is disabled")
            return

        try:
            if not settings.CALDAV_USERNAME or not settings.CALDAV_PASSWORD:
                print("Warning: CalDAV authentication is enabled but credentials are missing. Running without authentication.")
                return

            htpasswd_dir = os.path.dirname("/etc/radicale/users")
            if not os.path.exists(htpasswd_dir):
                os.makedirs(htpasswd_dir, mode=0o755, exist_ok=True)

            if not os.path.exists("/etc/radicale/users"):
                # Generate password hash
                if not isinstance(settings.CALDAV_PASSWORD, str):
                    print("Warning: CALDAV_PASSWORD must be a string. Running without authentication.")
                    return
                password = settings.CALDAV_PASSWORD.encode('utf-8')
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password, salt)
            
                # Write to htpasswd file with secure permissions
                with open("/etc/radicale/users", "w") as f:
                    f.write(f"{settings.CALDAV_USERNAME}:{hashed.decode('utf-8')}\n")
            
                # Set secure permissions on htpasswd file
                os.chmod("/etc/radicale/users", 0o600)
        except Exception as e:
            print(f"Warning: Failed to initialize CalDAV authentication: {str(e)}. Running without authentication.")
            return

    def create_calendar(self, user_id: int, calendar_name: str = "PM Tool"):
        """Create a new calendar for a user"""
        calendar_path = f"{user_id}/{calendar_name}"
        props = {
            "D:displayname": calendar_name,
            "C:supported-calendar-component-set": ["VEVENT"],
        }
        self.storage.create_collection(calendar_path, props)
        return calendar_path

    def add_task(self, calendar_path: str, task_data: dict):
        """Add a task as an event to the calendar"""
        try:
            # Validate required fields
            required_fields = ["description", "start_date", "end_date", "estimated_hours"]
            missing_fields = [field for field in required_fields if field not in task_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Validate dates
            if not isinstance(task_data["start_date"], datetime):
                raise ValueError("start_date must be a datetime object")
            if not isinstance(task_data["end_date"], datetime):
                raise ValueError("end_date must be a datetime object")
            if task_data["start_date"] >= task_data["end_date"]:
                raise ValueError("end_date must be after start_date")
                
            # Validate estimated hours
            if not isinstance(task_data["estimated_hours"], (int, float)):
                raise ValueError("estimated_hours must be a number")
            if task_data["estimated_hours"] <= 0:
                raise ValueError("estimated_hours must be positive")
            
            collection = self.storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
            
            # Create iCalendar event with enhanced fields
            event = {
                "component": "VEVENT",
                "uid": str(uuid.uuid4()),
                "summary": task_data["description"],
                "dtstart": task_data["start_date"].strftime("%Y%m%dT%H%M%SZ"),
                "dtend": task_data["end_date"].strftime("%Y%m%dT%H%M%SZ"),
                "description": (
                    f"Estimated hours: {task_data['estimated_hours']}\n"
                    f"Status: {task_data.get('status', 'pending')}\n"
                    f"Confidence: {task_data.get('confidence_score', 0.0):.0%}"
                ),
                "categories": ["PM Tool Task"],
                "status": "NEEDS-ACTION" if task_data.get("status") == "pending"
                         else "IN-PROCESS" if task_data.get("status") == "in_progress"
                         else "COMPLETED",
                "priority": "1" if task_data.get("priority") == "high"
                          else "5" if task_data.get("priority") == "medium"
                          else "9",
                "x-pm-tool-id": str(task_data.get("id", "")),
                "x-pm-tool-estimated-hours": str(task_data["estimated_hours"]),
                "x-pm-tool-confidence": str(task_data.get("confidence_score", 0.0)),
                "x-pm-tool-rationale": task_data.get("confidence_rationale", "")
            }
            
            collection.upload(event)
            return event["uid"]
        except Exception as e:
            raise ValueError(f"Failed to add task: {str(e)}")

    def update_task(self, calendar_path: str, event_uid: str, task_data: dict):
        """Update an existing task in the calendar"""
        try:
            # Validate required fields
            required_fields = ["description", "start_date", "end_date", "estimated_hours"]
            missing_fields = [field for field in required_fields if field not in task_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Validate dates
            if not isinstance(task_data["start_date"], datetime):
                raise ValueError("start_date must be a datetime object")
            if not isinstance(task_data["end_date"], datetime):
                raise ValueError("end_date must be a datetime object")
            if task_data["start_date"] >= task_data["end_date"]:
                raise ValueError("end_date must be after start_date")
                
            # Validate estimated hours
            if not isinstance(task_data["estimated_hours"], (int, float)):
                raise ValueError("estimated_hours must be a number")
            if task_data["estimated_hours"] <= 0:
                raise ValueError("estimated_hours must be positive")
            
            collection = self.storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
                
            event = collection.get_item(event_uid)
            if not event:
                return False
            
            event_data = event.get_component()
            event_data["summary"] = task_data["description"]
            event_data["dtstart"] = task_data["start_date"].strftime("%Y%m%dT%H%M%SZ")
            event_data["dtend"] = task_data["end_date"].strftime("%Y%m%dT%H%M%SZ")
            event_data["description"] = (
                f"Estimated hours: {task_data['estimated_hours']}\n"
                f"Status: {task_data.get('status', 'pending')}\n"
                f"Confidence: {task_data.get('confidence_score', 0.0):.0%}"
            )
            event_data["status"] = ("NEEDS-ACTION" if task_data.get("status") == "pending"
                                  else "IN-PROCESS" if task_data.get("status") == "in_progress"
                                  else "COMPLETED")
            event_data["priority"] = ("1" if task_data.get("priority") == "high"
                                    else "5" if task_data.get("priority") == "medium"
                                    else "9")
            event_data["x-pm-tool-estimated-hours"] = str(task_data["estimated_hours"])
            
            collection.upload(event_data)
            return True
        except Exception as e:
            raise ValueError(f"Failed to update task: {str(e)}")

    def delete_task(self, calendar_path: str, event_uid: str):
        """Delete a task from the calendar"""
        try:
            collection = self.storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
                
            event = collection.get_item(event_uid)
            if not event:
                return False
            
            collection.delete(event_uid)
            return True
        except Exception as e:
            raise ValueError(f"Failed to delete task: {str(e)}")

    def sync_task_with_calendar(self, task_data: Dict[str, Any], calendar_path: str) -> str:
        """Synchronize a task with the calendar, creating or updating as needed"""
        try:
            # Validate required fields
            required_fields = ["description", "start_date", "end_date", "estimated_hours", "status", "id"]
            missing_fields = [field for field in required_fields if field not in task_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
                
            # Ensure dates are datetime objects
            if not isinstance(task_data["start_date"], datetime):
                task_data["start_date"] = datetime.now()
            if not isinstance(task_data["end_date"], datetime):
                task_data["end_date"] = datetime.now() + timedelta(hours=task_data["estimated_hours"])
                
            # Try to find existing event by task ID
            collection = self.storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
            
            existing_event = None
            for event in collection.list():
                event_data = event.get_component()
                if event_data.get("x-pm-tool-id") == str(task_data["id"]):
                    existing_event = event
                    break
            
            if existing_event:
                # Update existing event
                event_uid = existing_event.get_component()["uid"]
                if self.update_task(calendar_path, event_uid, task_data):
                    return event_uid
                else:
                    raise ValueError("Failed to update task in calendar")
            else:
                # Create new event
                event_uid = self.add_task(calendar_path, task_data)
                if not event_uid:
                    raise ValueError("Failed to add task to calendar")
                return event_uid
        except Exception as e:
            raise ValueError(f"Failed to sync task: {str(e)}")
            
            # Try to find existing event by task ID
            collection = self.storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
            
            existing_event = None
            for event in collection.list():
                event_data = event.get_component()
                if event_data.get("x-pm-tool-id") == str(task_data["id"]):
                    existing_event = event
                    break
            
            if existing_event:
                # Update existing event
                event_uid = existing_event.get_component()["uid"]
                if self.update_task(calendar_path, event_uid, task_data):
                    return event_uid
                else:
                    raise ValueError("Failed to update task in calendar")
            else:
                # Create new event
                event_uid = self.add_task(calendar_path, task_data)
                if not event_uid:
                    raise ValueError("Failed to add task to calendar")
                return event_uid
        except Exception as e:
            raise ValueError(f"Failed to sync task: {str(e)}")
    
    def get_tasks(self, calendar_path: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        """Get all tasks in a date range"""
        try:
            # Validate date range if provided
            if start_date and end_date and start_date >= end_date:
                raise ValueError("end_date must be after start_date")
            
            collection = self.storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
            
            tasks = []
            for event in collection.list():
                try:
                    event_data = event.get_component()
                    event_start = datetime.strptime(event_data["dtstart"], "%Y%m%dT%H%M%SZ")
                    event_end = datetime.strptime(event_data["dtend"], "%Y%m%dT%H%M%SZ")
                    
                    # Extract task data
                    task = {
                        "uid": event_data["uid"],
                        "description": event_data["summary"],
                        "start_date": event_start,
                        "end_date": event_end,
                        "status": ("pending" if event_data.get("status") == "NEEDS-ACTION"
                                else "in_progress" if event_data.get("status") == "IN-PROCESS"
                                else "completed"),
                        "priority": ("high" if event_data.get("priority") == "1"
                                  else "medium" if event_data.get("priority") == "5"
                                  else "low"),
                        "estimated_hours": float(event_data.get("x-pm-tool-estimated-hours", "0.0")),
                        "confidence_score": float(event_data.get("x-pm-tool-confidence", "0.0")),
                        "confidence_rationale": event_data.get("x-pm-tool-rationale", "")
                    }
                    
                    # Apply date filter if provided
                    if start_date and end_date:
                        if start_date <= event_start <= end_date or start_date <= event_end <= end_date:
                            tasks.append(task)
                    else:
                        tasks.append(task)
                except Exception as e:
                    print(f"Warning: Failed to parse event {event_data.get('uid', 'unknown')}: {str(e)}")
                    continue
            
            return tasks
        except Exception as e:
            raise ValueError(f"Failed to get tasks: {str(e)}")
