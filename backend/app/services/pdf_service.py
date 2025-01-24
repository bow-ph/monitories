from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from app.models.invoice import Invoice
import os

def generate_invoice_pdf(invoice: Invoice) -> str:
    """Generate PDF invoice and return the path to the generated file"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(invoice.pdf_path), exist_ok=True)
    
    # Create PDF
    c = canvas.Canvas(invoice.pdf_path, pagesize=A4)
    width, height = A4
    
    # Company Logo
    # Try multiple possible logo paths
    logo_paths = [
        os.path.join(os.path.dirname(__file__), "..", "static", "logo.png"),  # Production path
        os.path.join(os.path.dirname(invoice.pdf_path), "static", "logo.png"),  # Test path
        os.path.join(os.path.dirname(__file__), "..", "..", "static", "logo.png")  # Root path
    ]
    
    logo_added = False
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, 50, height - 150, width=200, preserveAspectRatio=True)
                logo_added = True
                break
            except Exception as e:
                print(f"Warning: Failed to load logo from {logo_path}: {str(e)}")
                continue
    
    if not logo_added:
        # Add company name as text if no logo is available
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 150, "PM Tool")
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 200, "Rechnung")
    
    # Invoice Details
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 250, f"Rechnungsnummer: {invoice.invoice_number}")
    c.drawString(50, height - 270, f"Datum: {invoice.issue_date.strftime('%d.%m.%Y')}")
    
    # Financial Information
    y = height - 350
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Betrag")
    c.drawString(200, y, "Netto")
    c.drawString(300, y, "MwSt.")
    c.drawString(400, y, "Brutto")
    
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(50, y, "Abonnement")
    c.drawString(200, y, f"{invoice.currency} {invoice.net_amount:.2f}")
    c.drawString(300, y, f"{invoice.currency} {invoice.vat_amount:.2f}")
    c.drawString(400, y, f"{invoice.currency} {invoice.total_amount:.2f}")
    
    if invoice.vat_rate > 0:
        c.drawString(300, y + 15, f"({invoice.vat_rate * 100:.0f}%)")
    
    # Total
    y -= 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Gesamtbetrag:")
    c.drawString(400, y, f"{invoice.currency} {invoice.total_amount:.2f}")
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Vielen Dank für Ihr Vertrauen!")
    
    c.save()
    return invoice.pdf_path
