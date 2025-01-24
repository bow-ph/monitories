from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.core.database import get_db
from app.services.pdf_analysis_service import PDFAnalysisService
from app.services.estimation_service import EstimationService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/{project_id}/analyze-pdf")
async def analyze_pdf(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Analyze a PDF file to extract tasks and time estimates
    
    Args:
        project_id: ID of the project
        file: PDF file to analyze
        db: Database session
        
    Returns:
        dict: Analysis results including tasks and estimates
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    pdf_service = PDFAnalysisService(db)
    result = await pdf_service.analyze_pdf(project_id, file)
    return result

@router.get("/{project_id}/proactive-hints")
async def get_proactive_hints(
    project_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get proactive hints about financial and time impact for a project
    
    Args:
        project_id: ID of the project
        db: Database session
        
    Returns:
        dict: Analysis results including financial impact and recommendations
    """
    try:
        estimation_service = EstimationService(db)
        result = await estimation_service.generate_proactive_hints(project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating proactive hints: {str(e)}")
