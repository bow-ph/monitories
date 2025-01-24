from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import Invoice as InvoiceSchema
from app.core.auth import get_current_user
from app.models.user import User
import os

router = APIRouter()

@router.get("/invoices", response_model=List[InvoiceSchema])
async def list_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all invoices for the current user"""
    invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).all()
    return invoices

@router.get("/invoices/{invoice_id}/download")
async def download_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a specific invoice PDF"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if not invoice.pdf_path or not os.path.exists(invoice.pdf_path):
        raise HTTPException(status_code=404, detail="Invoice PDF not found")
        
    return FileResponse(
        invoice.pdf_path,
        media_type="application/pdf",
        filename=f"rechnung_{invoice.invoice_number}.pdf"
    )
