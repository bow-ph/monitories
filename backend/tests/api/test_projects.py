import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.projects import router
from fastapi import FastAPI
from app.core.database import get_db
import io

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture
def db_session():
    return MagicMock()

def get_test_db():
    return db_session

app.dependency_overrides[get_db] = get_test_db

def test_analyze_pdf_endpoint():
    content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(content), "application/pdf")}
    
    mock_response = {
        "status": "success",
        "tasks": [
            {
                "description": "Test task",
                "estimated_hours": 4.0,
                "confidence_score": 0.8
            }
        ],
        "total_estimated_hours": 4.0,
        "risk_factors": ["Test risk"]
    }
    
    with patch('app.services.pdf_analysis_service.PDFAnalysisService.analyze_pdf', 
              return_value=mock_response):
        response = client.post("/projects/1/analyze-pdf", files=files)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert len(result["tasks"]) == 1

def test_analyze_pdf_invalid_file():
    files = {"file": ("test.txt", io.BytesIO(b""), "text/plain")}
    response = client.post("/projects/1/analyze-pdf", files=files)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_proactive_hints():
    mock_response = {
        "status": "success",
        "financial_impact": {
            "risk_level": "medium",
            "potential_cost_overrun": 1000.0
        },
        "time_impact": {
            "risk_level": "low",
            "potential_delay_hours": 8.0
        },
        "recommendations": [
            {
                "type": "cost",
                "description": "Test recommendation",
                "priority": "high"
            }
        ]
    }
    
    with patch('app.services.estimation_service.EstimationService.generate_proactive_hints',
              return_value=mock_response):
        response = client.get("/projects/1/proactive-hints")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "financial_impact" in result
        assert "time_impact" in result
        assert len(result["recommendations"]) == 1

@pytest.mark.asyncio
async def test_get_proactive_hints_error():
    with patch('app.services.estimation_service.EstimationService.generate_proactive_hints',
              side_effect=ValueError("Test error")):
        response = client.get("/projects/1/proactive-hints")
        assert response.status_code == 400
        assert "Test error" in response.json()["detail"]
