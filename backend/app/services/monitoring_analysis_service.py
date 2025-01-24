from typing import Dict, List, Optional
import os
from openai import OpenAI, APIError, RateLimitError
from fastapi import HTTPException
from datetime import datetime
from app.models.task import Task
from sqlalchemy.orm import Session

class MonitoringAnalysisService:
    """Service for analyzing monitoring data and creating tasks"""
    
    def __init__(self):
        """Initialize the OpenAI service with API key from environment"""
        self.api_key = os.getenv("Open_AI_API")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
        self.client = OpenAI(
            api_key=self.api_key,
            timeout=60.0,
            max_retries=2,
            default_headers={"User-Agent": "Monitories/1.0"}
        )
        
    async def analyze_monitoring_data(self, monitoring_data: Dict) -> Dict:
        """
        Analyze monitoring data to extract findings and potential tasks
        
        Args:
            monitoring_data (Dict): The monitoring data including system analysis,
                                  server status, security checks, etc.
            
        Returns:
            Dict: Contains analyzed findings and potential tasks
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are an IT systems monitoring assistant specialized in analyzing system data and identifying actionable tasks, with particular focus on detecting End-of-Life (EOL) components. Format your response as JSON with the following structure:
{
    "monitoring_analysis": {
        "system_health": "good|warning|critical",
        "context": "Brief description of system state",
        "severity_level": "low|medium|high|critical",
        "confidence_score": float (0-1)
    },
    "findings": [
        {
            "type": "security|performance|update|compliance",
            "description": "Finding description",
            "severity": "low|medium|high|critical",
            "confidence": float (0-1),
            "confidence_rationale": "Detailed explanation of confidence",
            "estimated_hours": float,
            "priority": "low|medium|high",
            "technical_details": {
                "component": "affected system component",
                "current_state": "current state description",
                "desired_state": "desired state description",
                "eol_date": "YYYY-MM-DD if component is approaching or past EOL",
                "days_until_eol": integer or null,
                "is_eol": boolean
            },
            "recommended_action": "Detailed action plan",
            "dependencies": ["list of dependencies"],
            "risks": ["list of potential risks"],
            "deadline": "YYYY-MM-DD for critical updates or EOL-related tasks"
        }
    ],
    "total_estimated_hours": float,
    "risk_assessment": {
        "overall_risk": "low|medium|high|critical",
        "confidence": float (0-1),
        "rationale": "Detailed risk explanation",
        "immediate_actions_required": boolean,
        "factors": {
            "security_risk": float (0-1),
            "performance_risk": float (0-1),
            "compliance_risk": float (0-1),
            "update_risk": float (0-1)
        }
    }
}"""},
                    {"role": "user", "content": f"Analyze this monitoring data and identify actionable tasks:\n\n{monitoring_data}"}
                ],
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            raise HTTPException(
                status_code=429,
                detail=f"OpenAI API rate limit exceeded: {str(e)}"
            )
        except APIError as e:
            status_code = getattr(e, 'status_code', 500)
            raise HTTPException(
                status_code=status_code,
                detail=f"OpenAI API error: {str(e)}"
            )

    def convert_findings_to_tasks(self, findings: List[Dict], project_id: int, db: Session) -> List[Task]:
        """
        Convert monitoring findings into actionable tasks, with special handling for EOL components
        
        Args:
            findings (List[Dict]): List of findings from monitoring analysis
            project_id (int): ID of the project to associate tasks with
            db (Session): Database session
            
        Returns:
            List[Task]: List of created tasks
        """
        if not findings:
            raise ValueError("No findings provided")
        if project_id <= 0:
            raise ValueError("Invalid project ID")
            
        tasks = []
        for finding in findings:
            # Map severity to priority
            priority_map = {
                "critical": "high",
                "high": "high",
                "medium": "medium",
                "low": "low"
            }
            
            # Build description with EOL information if available
            description = f"{finding['type'].upper()}: {finding['description']}"
            if finding.get('technical_details', {}).get('eol_date'):
                eol_date = finding['technical_details']['eol_date']
                days_until_eol = finding['technical_details'].get('days_until_eol')
                is_eol = finding['technical_details'].get('is_eol', False)
                
                if is_eol:
                    description += f"\n\n⚠️ COMPONENT HAS REACHED END OF LIFE ON {eol_date}"
                else:
                    description += f"\n\n⚠️ END OF LIFE APPROACHING: {eol_date} ({days_until_eol} days remaining)"
                    
            description += f"\n\nRecommended Action: {finding['recommended_action']}"
            
            # Create task with enhanced metadata
            task = Task(
                project_id=project_id,
                description=description,
                estimated_hours=finding['estimated_hours'],
                status="pending",
                priority=priority_map.get(finding['severity'], "medium"),
                confidence_score=finding['confidence'],
                confidence_rationale=f"Finding Type: {finding['type']}\nSeverity: {finding['severity']}\n\nRationale: {finding['confidence_rationale']}\n\nRisks: {', '.join(finding['risks'])}",
                finding_type=finding['type'],
                technical_details=finding.get('technical_details'),
                risks=finding.get('risks'),
                severity=finding['severity']
            )
            
            db.add(task)
            tasks.append(task)
            
        db.commit()
        return tasks
