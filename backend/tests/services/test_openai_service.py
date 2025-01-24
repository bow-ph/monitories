import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai import APIError, RateLimitError
from app.services.openai_service import OpenAIService
import json
import os

@pytest.fixture
def openai_service():
    with patch.dict(os.environ, {'Open_AI_API': 'test_key'}):
        with patch('app.services.openai_service.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock()
            mock_openai.return_value = mock_client
            service = OpenAIService()
            service.client = mock_client
            return service

@pytest.mark.asyncio
async def test_analyze_pdf_text(openai_service):
    # Create mock response
    response_content = {
        "tasks": [
            {
                "description": "Test task",
                "estimated_hours": 4.0,
                "confidence": 0.8,
                "dependencies": []
            }
        ],
        "total_estimated_hours": 4.0,
        "risk_factors": ["Test risk"]
    }
    
    mock_message = ChatCompletionMessage(
        role="assistant",
        content=json.dumps(response_content)
    )
    mock_choice = Choice(
        index=0,
        message=mock_message,
        finish_reason="stop"
    )
    mock_response = ChatCompletion(
        id="test_id",
        choices=[mock_choice],
        created=1234567890,
        model="gpt-4",
        object="chat.completion",
        system_fingerprint="test_fingerprint",
        usage={"completion_tokens": 100, "prompt_tokens": 50, "total_tokens": 150}
    )
    
    # Mock the create method
    openai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    # Test the service
    result = await openai_service.analyze_pdf_text("Test PDF content")
    result_dict = json.loads(result)
    
    # Verify the result
    assert "tasks" in result_dict
    assert len(result_dict["tasks"]) == 1
    assert result_dict["tasks"][0]["estimated_hours"] == 4.0
    assert result_dict["total_estimated_hours"] == 4.0
    
    # Verify the API was called correctly
    openai_service.client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_financial_impact(openai_service):
    # Create mock response
    response_content = {
        "financial_impact": {
            "risk_level": "medium",
            "potential_cost_overrun": 1000.0,
            "confidence": 0.7
        },
        "time_impact": {
            "risk_level": "low",
            "potential_delay_hours": 8.0,
            "confidence": 0.8
        },
        "recommendations": [
            {
                "type": "cost",
                "description": "Test recommendation",
                "priority": "high"
            }
        ]
    }
    
    mock_message = ChatCompletionMessage(
        role="assistant",
        content=json.dumps(response_content)
    )
    mock_choice = Choice(
        index=0,
        message=mock_message,
        finish_reason="stop"
    )
    mock_response = ChatCompletion(
        id="test_id",
        choices=[mock_choice],
        created=1234567890,
        model="gpt-4",
        object="chat.completion",
        system_fingerprint="test_fingerprint",
        usage={"completion_tokens": 100, "prompt_tokens": 50, "total_tokens": 150}
    )
    
    # Mock the create method
    openai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    # Test data
    project_stats = {"total_estimated_hours": 40}
    tasks = [{"description": "Test task", "estimated_hours": 4}]
    
    # Test the service
    result = await openai_service.analyze_financial_impact(project_stats, tasks)
    result_dict = json.loads(result)
    
    # Verify the result
    assert "financial_impact" in result_dict
    assert result_dict["financial_impact"]["risk_level"] == "medium"
    assert "time_impact" in result_dict
    assert len(result_dict["recommendations"]) == 1
    
    # Verify the API was called correctly
    openai_service.client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_validate_time_estimates(openai_service):
    # Create mock response
    response_content = {
        "validated_tasks": [
            {
                "task_id": "1",
                "original_estimate": 4.0,
                "suggested_estimate": 5.0,
                "confidence": 0.8,
                "adjustment_reason": "Test reason"
            }
        ],
        "overall_assessment": {
            "estimation_quality": "good",
            "suggestions": ["Test suggestion"]
        }
    }
    
    mock_message = ChatCompletionMessage(
        role="assistant",
        content=json.dumps(response_content)
    )
    mock_choice = Choice(
        index=0,
        message=mock_message,
        finish_reason="stop"
    )
    mock_response = ChatCompletion(
        id="test_id",
        choices=[mock_choice],
        created=1234567890,
        model="gpt-4",
        object="chat.completion",
        system_fingerprint="test_fingerprint",
        usage={"completion_tokens": 100, "prompt_tokens": 50, "total_tokens": 150}
    )
    
    # Mock the create method
    openai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    # Test data
    tasks = [{"id": "1", "description": "Test task", "estimated_hours": 4}]
    
    # Test the service
    result = await openai_service.validate_time_estimates(tasks)
    result_dict = json.loads(result)
    
    # Verify the result
    assert "validated_tasks" in result_dict
    assert len(result_dict["validated_tasks"]) == 1
    assert "overall_assessment" in result_dict
    
    # Verify the API was called correctly
    openai_service.client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_openai_rate_limit_error(openai_service):
    # Mock rate limit error
    error = RateLimitError(
        message="Rate limit exceeded",
        response=MagicMock(status_code=429),
        body={"error": {"message": "Rate limit exceeded"}}
    )
    
    # Set up the mock to raise the error
    openai_service.client.chat.completions.create = AsyncMock(side_effect=error)
    
    # Test the error handling
    with pytest.raises(HTTPException) as exc_info:
        await openai_service.analyze_pdf_text("Test content")
    assert exc_info.value.status_code == 429
    assert "OpenAI API rate limit exceeded" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_openai_api_error(openai_service):
    # Mock internal server error
    error = APIError(
        message="Internal server error",
        request=MagicMock(method="POST", url="https://api.openai.com/v1/chat/completions"),
        body={"error": {"message": "Internal server error", "type": "internal_server_error"}}
    )
    
    # Set up the mock to raise the error
    openai_service.client.chat.completions.create = AsyncMock(side_effect=error)
    
    # Test the error handling
    with pytest.raises(HTTPException) as exc_info:
        await openai_service.analyze_pdf_text("Test content")
    assert exc_info.value.status_code == 500
    assert "OpenAI API error" in str(exc_info.value.detail)
