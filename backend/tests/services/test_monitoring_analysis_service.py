import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.monitoring_analysis_service import MonitoringAnalysisService
from app.models.task import Task
from sqlalchemy.orm import Session

@pytest.fixture
def mock_openai_response():
    return {
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
                "confidence_rationale": "Clear version detection with known EOL date",
                "estimated_hours": 4.0,
                "priority": "high",
                "technical_details": {
                    "component": "Node.js",
                    "current_state": "14.21.3",
                    "desired_state": "20.x LTS"
                },
                "recommended_action": "Upgrade Node.js to latest LTS version",
                "dependencies": ["package.json updates", "dependency compatibility check"],
                "risks": ["Potential breaking changes in dependencies"]
            },
            {
                "type": "security",
                "description": "Outdated SSL certificate configuration",
                "severity": "critical",
                "confidence": 0.9,
                "confidence_rationale": "Direct SSL configuration analysis",
                "estimated_hours": 2.0,
                "priority": "high",
                "technical_details": {
                    "component": "SSL Configuration",
                    "current_state": "TLS 1.1",
                    "desired_state": "TLS 1.3"
                },
                "recommended_action": "Update SSL configuration to use TLS 1.3",
                "dependencies": [],
                "risks": ["Temporary service interruption during update"]
            }
        ],
        "total_estimated_hours": 6.0,
        "risk_assessment": {
            "overall_risk": "high",
            "confidence": 0.9,
            "rationale": "Multiple critical components require immediate attention",
            "immediate_actions_required": True,
            "factors": {
                "security_risk": 0.8,
                "performance_risk": 0.4,
                "compliance_risk": 0.7,
                "update_risk": 0.6
            }
        }
    }

@pytest.fixture
def monitoring_service():
    return MonitoringAnalysisService()

@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)

@pytest.mark.asyncio
async def test_analyze_monitoring_data(monitoring_service, mock_openai_response):
    with patch('app.services.monitoring_analysis_service.OpenAI') as mock_openai:
        # Configure mock
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content=mock_openai_response))]
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        # Test data
        monitoring_data = {
            "system": {
                "nodejs_version": "14.21.3",
                "ssl_config": "TLS 1.1",
                "last_update": "2023-12-01"
            }
        }

        # Execute
        result = await monitoring_service.analyze_monitoring_data(monitoring_data)

        # Verify
        assert result["monitoring_analysis"]["system_health"] == "warning"
        assert len(result["findings"]) == 2
        assert result["findings"][0]["type"] == "update"
        assert result["findings"][1]["type"] == "security"
        assert result["risk_assessment"]["overall_risk"] == "high"

def test_convert_findings_to_tasks(monitoring_service, mock_openai_response, mock_db_session):
    # Test data
    findings = mock_openai_response["findings"]
    project_id = 1

    # Execute
    tasks = monitoring_service.convert_findings_to_tasks(findings, project_id, mock_db_session)

    # Verify
    assert len(tasks) == 2
    
    # Verify Node.js update task
    nodejs_task = tasks[0]
    assert nodejs_task.project_id == project_id
    assert "Node.js" in nodejs_task.description
    assert nodejs_task.estimated_hours == 4.0
    assert nodejs_task.priority == "high"
    assert nodejs_task.confidence_score == 0.95
    assert nodejs_task.finding_type == "update"
    assert "current_state" in nodejs_task.technical_details
    assert len(nodejs_task.risks) > 0
    assert nodejs_task.severity == "high"

    # Verify SSL update task
    ssl_task = tasks[1]
    assert ssl_task.project_id == project_id
    assert "SSL" in ssl_task.description
    assert ssl_task.estimated_hours == 2.0
    assert ssl_task.priority == "high"
    assert ssl_task.confidence_score == 0.9
    assert ssl_task.finding_type == "security"
    assert ssl_task.severity == "critical"

@pytest.mark.asyncio
async def test_analyze_monitoring_data_with_eol(monitoring_service, mock_db_session):
    with patch('app.services.monitoring_analysis_service.OpenAI') as mock_openai:
        # Mock response including EOL information
        eol_response = {
            "monitoring_analysis": {
                "system_health": "warning",
                "context": "EOL components detected",
                "severity_level": "high",
                "confidence_score": 0.9
            },
            "findings": [
                {
                    "type": "update",
                    "description": "PHP 7.4 detected - End of Life reached",
                    "severity": "critical",
                    "confidence": 0.95,
                    "confidence_rationale": "PHP 7.4 EOL date: November 28, 2023",
                    "estimated_hours": 8.0,
                    "priority": "high",
                    "technical_details": {
                        "component": "PHP",
                        "current_state": "7.4.33",
                        "desired_state": "8.2",
                        "eol_date": "2023-11-28"
                    },
                    "recommended_action": "Upgrade PHP to version 8.2",
                    "dependencies": ["Framework compatibility check", "Code updates"],
                    "risks": ["Breaking changes in PHP 8.x"]
                }
            ]
        }
        
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content=eol_response))]
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        # Test data with EOL component
        monitoring_data = {
            "system": {
                "php_version": "7.4.33",
                "last_update": "2023-06-01"
            }
        }

        # Execute
        result = await monitoring_service.analyze_monitoring_data(monitoring_data)

        # Verify EOL detection
        assert result["findings"][0]["type"] == "update"
        assert "EOL" in result["findings"][0]["description"]
        assert result["findings"][0]["severity"] == "critical"
        assert "eol_date" in result["findings"][0]["technical_details"]

        # Convert to tasks
        tasks = monitoring_service.convert_findings_to_tasks(result["findings"], project_id=1, db=mock_db_session)
        
        # Verify task creation with EOL information
        eol_task = tasks[0]
        assert eol_task.finding_type == "update"
        assert eol_task.severity == "critical"
        assert "PHP" in eol_task.description
        assert eol_task.priority == "high"
        assert "eol_date" in eol_task.technical_details

def test_error_handling(monitoring_service, mock_db_session):
    # Test invalid findings
    with pytest.raises(ValueError):
        monitoring_service.convert_findings_to_tasks([], project_id=1, db=mock_db_session)

    with pytest.raises(ValueError):
        monitoring_service.convert_findings_to_tasks(None, project_id=1, db=mock_db_session)

    # Test invalid project ID
    invalid_findings = [{
        "type": "security",
        "description": "Test finding",
        "severity": "low",
        "confidence": 0.8,
        "estimated_hours": 1.0
    }]
    with pytest.raises(ValueError):
        monitoring_service.convert_findings_to_tasks(invalid_findings, project_id=-1, db=mock_db_session)
