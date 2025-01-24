from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.project import Project
from app.services.openai_service import OpenAIService

class EstimationService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_service = OpenAIService()

    def analyze_estimate_accuracy(self, task_id: int) -> Dict:
        """Analyze the accuracy of a task's time estimate"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")

        if task.actual_hours is None:
            return {
                "status": "incomplete",
                "message": "Task has not been completed yet"
            }

        deviation = task.actual_hours - task.estimated_hours
        deviation_percentage = (deviation / task.estimated_hours) * 100

        return {
            "status": "analyzed",
            "task_id": task.id,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "deviation_hours": deviation,
            "deviation_percentage": deviation_percentage,
            "accuracy_rating": self._calculate_accuracy_rating(deviation_percentage)
        }

    def _calculate_accuracy_rating(self, deviation_percentage: float) -> str:
        """Calculate accuracy rating based on deviation percentage"""
        if abs(deviation_percentage) <= 10:
            return "excellent"
        elif abs(deviation_percentage) <= 25:
            return "good"
        elif abs(deviation_percentage) <= 50:
            return "fair"
        else:
            return "poor"

    def get_project_estimation_stats(self, project_id: int) -> Dict:
        """Get estimation statistics for an entire project"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")

        tasks = self.db.query(Task).filter(
            Task.project_id == project_id,
            Task.actual_hours.isnot(None)
        ).all()

        if not tasks:
            return {
                "status": "incomplete",
                "message": "No completed tasks in project"
            }

        total_estimated = sum(task.estimated_hours for task in tasks)
        total_actual = sum(task.actual_hours for task in tasks)
        total_deviation = total_actual - total_estimated
        avg_deviation_percentage = (total_deviation / total_estimated) * 100

        task_accuracies = [
            self.analyze_estimate_accuracy(task.id)
            for task in tasks
        ]

        return {
            "status": "analyzed",
            "project_id": project_id,
            "total_tasks": len(tasks),
            "total_estimated_hours": total_estimated,
            "total_actual_hours": total_actual,
            "total_deviation_hours": total_deviation,
            "average_deviation_percentage": avg_deviation_percentage,
            "overall_accuracy_rating": self._calculate_accuracy_rating(avg_deviation_percentage),
            "task_accuracies": task_accuracies
        }

    def detect_estimation_patterns(self, user_id: int) -> Dict:
        """Detect patterns in estimation accuracy across all user projects"""
        projects = self.db.query(Project).filter(Project.user_id == user_id).all()
        if not projects:
            return {
                "status": "incomplete",
                "message": "No projects found for user"
            }

        project_stats = [
            self.get_project_estimation_stats(project.id)
            for project in projects
            if self.get_project_estimation_stats(project.id)["status"] == "analyzed"
        ]

        if not project_stats:
            return {
                "status": "incomplete",
                "message": "No completed projects with tasks found"
            }

        avg_deviation = sum(
            stats["average_deviation_percentage"]
            for stats in project_stats
        ) / len(project_stats)

        return {
            "status": "analyzed",
            "user_id": user_id,
            "total_projects_analyzed": len(project_stats),
            "average_deviation_percentage": avg_deviation,
            "overall_accuracy_rating": self._calculate_accuracy_rating(avg_deviation),
            "project_stats": project_stats,
            "recommendations": self._generate_recommendations(avg_deviation)
        }

    def _generate_recommendations(self, avg_deviation: float) -> List[str]:
        """Generate recommendations based on estimation patterns"""
        recommendations = []
        
        if avg_deviation > 0:
            recommendations.append(
                "You tend to underestimate task durations. Consider adding a buffer of "
                f"approximately {abs(avg_deviation):.1f}% to your estimates."
            )
        else:
            recommendations.append(
                "You tend to overestimate task durations. Consider reducing your estimates by "
                f"approximately {abs(avg_deviation):.1f}%."
            )

        if abs(avg_deviation) > 50:
            recommendations.append(
                "Your estimates show significant deviation. Consider breaking down tasks into "
                "smaller, more manageable units for better estimation accuracy."
            )

        if abs(avg_deviation) > 25:
            recommendations.append(
                "Track the specific factors that cause estimation inaccuracies and create a "
                "checklist to account for these factors in future estimates."
            )

        return recommendations

    async def generate_proactive_hints(self, project_id: int) -> Dict:
        """
        Generate proactive hints about financial and time impact for a project
        
        Args:
            project_id: The ID of the project to analyze
            
        Returns:
            Dict containing analysis results and recommendations
        """
        # Get project statistics and tasks
        project_stats = self.get_project_estimation_stats(project_id)
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        
        # Convert tasks to dictionary format
        task_data = [
            {
                "id": task.id,
                "description": task.description,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "status": task.status,
                "confidence_score": task.confidence_score
            }
            for task in tasks
        ]
        
        try:
            # Get financial impact analysis from OpenAI
            analysis = await self.openai_service.analyze_financial_impact(
                project_stats=project_stats,
                tasks=task_data
            )
            
            # Parse the response
            try:
                if isinstance(analysis, str):
                    analysis_result = json.loads(analysis)
                else:
                    analysis_result = analysis
            except json.JSONDecodeError:
                raise ValueError("Invalid response format from OpenAI")
                
            # Validate time estimates if we have enough data
            if len(tasks) > 0:
                validation_result = await self.openai_service.validate_time_estimates(
                    tasks=task_data,
                    historical_data=self.detect_estimation_patterns(project_stats["project_id"])
                )
                if isinstance(validation_result, str):
                    validation_data = json.loads(validation_result)
                else:
                    validation_data = validation_result
                    
                analysis_result["time_validation"] = validation_data
            
            return {
                "status": "success",
                "financial_impact": analysis_result.get("financial_impact", {}),
                "time_impact": analysis_result.get("time_impact", {}),
                "recommendations": analysis_result.get("recommendations", []),
                "time_validation": analysis_result.get("time_validation", {})
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating proactive hints: {str(e)}"
            }
