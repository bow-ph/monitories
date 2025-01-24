from typing import Dict, List, Optional
import os
from openai import OpenAI, APIError, RateLimitError
from fastapi import HTTPException

class OpenAIService:
    """Service for handling OpenAI API interactions"""
    
    def __init__(self):
        """Initialize the OpenAI service with API key from environment"""
        self.api_key = os.getenv("Open_AI_API")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
        self.client = OpenAI(
            api_key=self.api_key,
            timeout=60.0,
            max_retries=2,
            default_headers={"User-Agent": "DocuPlanAI/1.0"}
        )
        
    async def analyze_pdf_text(self, text: str) -> Dict:
        """
        Analyze PDF text to extract tasks and time estimates
        
        Args:
            text (str): The extracted text from the PDF
            
        Returns:
            Dict: Contains extracted tasks and their time estimates
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a project management assistant specialized in analyzing project documents and extracting tasks with time estimates. You have expertise in identifying document types and understanding their context. Format your response as JSON with the following structure:
{
    "document_analysis": {
        "type": "quote|order|proposal|specification|other",
        "context": "Brief description of document context and purpose",
        "client_type": "agency|business|individual",
        "complexity_level": "low|medium|high",
        "clarity_score": float (0-1)
    },
    "tasks": [
        {
            "description": "Task description",
            "estimated_hours": float,
            "confidence": float (0-1),
            "confidence_rationale": "Detailed explanation including task clarity, dependencies, and risks",
            "dependencies": ["other task descriptions"],
            "complexity": "low|medium|high",
            "requires_client_input": boolean,
            "technical_requirements": ["list of technical requirements"],
            "deliverables": ["list of expected deliverables"]
        }
    ],
    "total_estimated_hours": float,
    "risk_factors": ["list of potential risks"],
    "confidence_analysis": {
        "overall_confidence": float (0-1),
        "rationale": "Detailed explanation of overall confidence",
        "improvement_suggestions": ["List of suggestions"],
        "accuracy_factors": {
            "document_clarity": float (0-1),
            "technical_complexity": float (0-1),
            "dependency_risk": float (0-1),
            "client_input_risk": float (0-1)
        }
    }
}"""},
                    {"role": "user", "content": f"Extract tasks and time estimates from this project document:\n\n{text}"}
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
            
    async def analyze_financial_impact(self, project_stats: Dict, tasks: List[Dict]) -> Dict:
        """
        Analyze financial impact and provide proactive hints based on project statistics and tasks
        
        Args:
            project_stats (Dict): Current project statistics
            tasks (List[Dict]): List of tasks with their estimates and actual times
            
        Returns:
            Dict: Contains financial impact analysis and recommendations
        """
        try:
            # Prepare the data for OpenAI
            context = {
                "project_stats": project_stats,
                "tasks": tasks
            }
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a project management advisor specialized in financial and time impact analysis. Format your response as JSON with the following structure:
{
    "financial_impact": {
        "risk_level": "low|medium|high",
        "potential_cost_overrun": float,
        "confidence": float (0-1)
    },
    "time_impact": {
        "risk_level": "low|medium|high",
        "potential_delay_hours": float,
        "confidence": float (0-1)
    },
    "recommendations": [
        {
            "type": "cost|time|resource",
            "description": "Detailed recommendation",
            "priority": "low|medium|high"
        }
    ]
}"""},
                    {"role": "user", "content": f"Analyze the financial and time impact for this project data:\n\n{context}"}
                ],
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except RateLimitError:
            raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded")
        except APIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
            
    async def validate_time_estimates(self, tasks: List[Dict], historical_data: Optional[Dict] = None) -> Dict:
        """
        Validate time estimates for tasks using AI and historical data if available
        
        Args:
            tasks (List[Dict]): List of tasks with their estimates
            historical_data (Optional[Dict]): Historical project data for reference
            
        Returns:
            Dict: Contains validation results and suggestions
        """
        try:
            context = {
                "tasks": tasks,
                "historical_data": historical_data
            }
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a project estimation validator. Format your response as JSON with the following structure:
{
    "validated_tasks": [
        {
            "task_id": "original task id",
            "original_estimate": float,
            "suggested_estimate": float,
            "confidence": float (0-1),
            "adjustment_reason": "explanation"
        }
    ],
    "overall_assessment": {
        "estimation_quality": "good|needs_review|poor",
        "suggestions": ["list of suggestions"]
    }
}"""},
                    {"role": "user", "content": f"Validate these time estimates based on the provided context:\n\n{context}"}
                ],
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except RateLimitError:
            raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded")
        except APIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
