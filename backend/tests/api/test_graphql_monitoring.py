import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch
from app.main import app
from app.models.task import Task
from app.models.user import User
from app.core.auth import create_access_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def test_user():
    return User(
        id=1,
        email="test@monitories.test",
        is_active=True,
        subscription_type="team"
    )

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}

def test_analyze_system(client, auth_headers, mock_db):
    # Test data
    monitoring_data = {
        "query": """
        mutation AnalyzeSystem($systemId: ID!, $monitoringData: MonitoringDataInput!) {
            analyzeSystem(systemId: $systemId, monitoringData: $monitoringData) {
                systemHealth
                context
                severityLevel
                confidenceScore
                findings {
                    type
                    description
                    severity
                    confidence
                    estimatedHours
                    technicalDetails {
                        component
                        currentState
                        desiredState
                        eolDate
                        daysUntilEol
                        isEol
                    }
                }
                riskAssessment {
                    overallRisk
                    confidence
                    immediateActionsRequired
                    factors {
                        securityRisk
                        performanceRisk
                        complianceRisk
                        updateRisk
                    }
                }
            }
        }
        """,
        "variables": {
            "systemId": "1",
            "monitoringData": {
                "system": {
                    "nodejs_version": "14.21.3",
                    "ssl_config": "TLS 1.1",
                    "last_update": "2023-12-01"
                }
            }
        }
    }

    with patch('app.services.monitoring_analysis_service.MonitoringAnalysisService') as MockService:
        mock_service = MockService.return_value
        mock_service.analyze_monitoring_data.return_value = {
            "monitoring_analysis": {
                "system_health": "warning",
                "context": "Multiple outdated components detected",
                "severity_level": "medium",
                "confidence_score": 0.85
            },
            "findings": [
                {
                    "type": "update",
                    "description": "Node.js version 14.x detected - End of Life approaching",
                    "severity": "high",
                    "confidence": 0.95,
                    "estimated_hours": 4.0,
                    "technical_details": {
                        "component": "Node.js",
                        "current_state": "14.21.3",
                        "desired_state": "20.x LTS",
                        "eol_date": "2024-04-30",
                        "days_until_eol": 120,
                        "is_eol": False
                    }
                }
            ]
        }

        response = client.post(
            "/graphql",
            json=monitoring_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        result = data["data"]["analyzeSystem"]
        assert result["systemHealth"] == "warning"
        assert len(result["findings"]) == 1
        assert result["findings"][0]["type"] == "update"
        assert "Node.js" in result["findings"][0]["description"]

def test_create_monitoring_tasks(client, auth_headers, mock_db):
    # Test data
    task_data = {
        "query": """
        mutation CreateMonitoringTasks($systemId: ID!, $findings: [MonitoringFinding!]!) {
            createMonitoringTasks(systemId: $systemId, findings: $findings) {
                id
                description
                estimatedHours
                status
                priority
                confidenceScore
                findingType
                technicalDetails
                severity
            }
        }
        """,
        "variables": {
            "systemId": "1",
            "findings": [
                {
                    "type": "update",
                    "description": "Node.js update required",
                    "severity": "high",
                    "confidence": 0.95,
                    "estimatedHours": 4.0,
                    "technicalDetails": {
                        "component": "Node.js",
                        "currentState": "14.21.3",
                        "desiredState": "20.x LTS",
                        "eolDate": "2024-04-30",
                        "daysUntilEol": 120,
                        "isEol": False
                    }
                }
            ]
        }
    }

    with patch('app.services.monitoring_analysis_service.MonitoringAnalysisService') as MockService:
        mock_service = MockService.return_value
        mock_task = Task(
            id=1,
            project_id=1,
            description="UPDATE: Node.js update required",
            estimated_hours=4.0,
            status="pending",
            priority="high",
            confidence_score=0.95,
            finding_type="update",
            technical_details={
                "component": "Node.js",
                "current_state": "14.21.3",
                "desired_state": "20.x LTS",
                "eol_date": "2024-04-30"
            },
            severity="high"
        )
        mock_service.convert_findings_to_tasks.return_value = [mock_task]

        response = client.post(
            "/graphql",
            json=task_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        tasks = data["data"]["createMonitoringTasks"]
        assert len(tasks) == 1
        assert tasks[0]["findingType"] == "update"
        assert tasks[0]["severity"] == "high"
        assert tasks[0]["priority"] == "high"

def test_query_monitoring_tasks(client, auth_headers, mock_db):
    # Test data
    query = {
        "query": """
        query MonitoringTasks($systemId: ID, $status: String) {
            monitoringTasks(systemId: $systemId, status: $status) {
                id
                description
                estimatedHours
                status
                priority
                confidenceScore
                findingType
                technicalDetails
                severity
            }
        }
        """,
        "variables": {
            "systemId": "1",
            "status": "pending"
        }
    }

    mock_tasks = [
        Task(
            id=1,
            project_id=1,
            description="UPDATE: Node.js update required",
            estimated_hours=4.0,
            status="pending",
            priority="high",
            confidence_score=0.95,
            finding_type="update",
            technical_details={
                "component": "Node.js",
                "current_state": "14.21.3",
                "desired_state": "20.x LTS"
            },
            severity="high"
        )
    ]

    with patch('sqlalchemy.orm.Query') as MockQuery:
        mock_query = MockQuery.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_tasks

        response = client.post(
            "/graphql",
            json=query,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        tasks = data["data"]["monitoringTasks"]
        assert len(tasks) == 1
        assert tasks[0]["findingType"] == "update"
        assert tasks[0]["status"] == "pending"
        assert tasks[0]["priority"] == "high"
