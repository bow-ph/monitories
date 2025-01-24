import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile, HTTPException
from app.services.pdf_analysis_service import PDFAnalysisService
import io
import json

@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def pdf_service(db_session):
    with patch('app.services.openai_service.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock()
        mock_openai.return_value = mock_client
        service = PDFAnalysisService(db_session)
        return service

@pytest.fixture
def mock_pdf_file():
    content = b"%PDF-1.4\nTest PDF content"
    return UploadFile(filename="test.pdf", file=io.BytesIO(content))

@pytest.mark.asyncio
async def test_extract_text_from_pdf(pdf_service, mock_pdf_file):
    with patch('pdfplumber.open') as mock_plumber:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_plumber.return_value.__enter__.return_value.pages = [mock_page]
        
        result = await pdf_service.extract_text_from_pdf(mock_pdf_file)
        assert result.strip() == "Test PDF content"

@pytest.mark.asyncio
async def test_analyze_pdf(pdf_service, mock_pdf_file, db_session):
    mock_openai_response = json.dumps({
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
    })
    
    with patch('pdfplumber.open') as mock_plumber, \
         patch('app.services.openai_service.OpenAIService.analyze_pdf_text', return_value=mock_openai_response):
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_plumber.return_value.__enter__.return_value.pages = [mock_page]
        
        result = await pdf_service.analyze_pdf(1, mock_pdf_file)
        
        assert result["status"] == "success"
        assert len(result["tasks"]) == 1
        assert result["total_estimated_hours"] == 4.0
        
        # Verify task was saved to database
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_file_type(pdf_service):
    invalid_file = UploadFile(filename="test.txt", file=io.BytesIO(b""))
    with pytest.raises(HTTPException) as exc_info:
        await pdf_service.extract_text_from_pdf(invalid_file)
    assert exc_info.value.status_code == 400
    assert "Invalid file type" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_pdf_extraction_error(pdf_service, mock_pdf_file):
    with patch('pdfplumber.open') as mock_plumber:
        mock_plumber.side_effect = Exception("PDF error")
        with pytest.raises(HTTPException) as exc_info:
            await pdf_service.extract_text_from_pdf(mock_pdf_file)
        assert exc_info.value.status_code == 400
        assert "Error processing PDF: PDF error" in str(exc_info.value.detail)
