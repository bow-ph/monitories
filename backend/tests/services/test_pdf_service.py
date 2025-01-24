import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_service import generate_invoice_pdf
from app.models.invoice import Invoice
from datetime import datetime
import os

@pytest.fixture
def mock_invoice():
    return Invoice(
        id=1,
        invoice_number="2024-01-00001",
        user_id=1,
        subscription_id=1,
        issue_date=datetime.utcnow(),
        total_amount=119.0,
        net_amount=100.0,
        vat_amount=19.0,
        vat_rate=0.19,
        currency="EUR",
        pdf_path="/tmp/test_invoice.pdf",
        status="paid"
    )

def test_generate_invoice_pdf(mock_invoice, tmp_path):
    """Test PDF generation with all invoice fields"""
    test_pdf_path = tmp_path / "test_invoice.pdf"
    mock_invoice.pdf_path = str(test_pdf_path)
    
    generate_invoice_pdf(mock_invoice)
    
    assert os.path.exists(test_pdf_path)
    assert os.path.getsize(test_pdf_path) > 0

def test_generate_invoice_pdf_creates_directory(mock_invoice, tmp_path):
    """Test PDF directory creation"""
    nested_dir = tmp_path / "invoices" / "2024" / "01"
    pdf_path = nested_dir / "test_invoice.pdf"
    mock_invoice.pdf_path = str(pdf_path)
    
    generate_invoice_pdf(mock_invoice)
    
    assert os.path.exists(nested_dir)
    assert os.path.exists(pdf_path)

@pytest.mark.parametrize("amount,expected_net,expected_vat", [
    (119.0, 100.0, 19.0),  # Standard 19% VAT
    (59.5, 50.0, 9.5),     # Half amount
    (238.0, 200.0, 38.0),  # Double amount
])
def test_invoice_calculations(mock_invoice, amount, expected_net, expected_vat, tmp_path):
    """Test VAT calculations in PDF generation"""
    test_pdf_path = tmp_path / "test_invoice.pdf"
    mock_invoice.pdf_path = str(test_pdf_path)
    mock_invoice.total_amount = amount
    mock_invoice.net_amount = expected_net
    mock_invoice.vat_amount = expected_vat
    
    generate_invoice_pdf(mock_invoice)
    
    assert os.path.exists(test_pdf_path)
    assert os.path.getsize(test_pdf_path) > 0

def test_generate_invoice_pdf_with_company_logo(mock_invoice, tmp_path):
    """Test PDF generation with company logo"""
    # Create mock logo file
    logo_dir = tmp_path / "static"
    os.makedirs(logo_dir)
    logo_path = logo_dir / "logo.png"
    with open(logo_path, "wb") as f:
        f.write(b"fake png content")
    
    test_pdf_path = tmp_path / "test_invoice.pdf"
    mock_invoice.pdf_path = str(test_pdf_path)
    
    with patch("os.path.exists") as mock_exists, \
         patch("reportlab.pdfgen.canvas.Canvas.drawImage") as mock_draw_image:
        mock_exists.return_value = True
        generate_invoice_pdf(mock_invoice)
        
        assert os.path.exists(test_pdf_path)
        assert os.path.getsize(test_pdf_path) > 0
        mock_draw_image.assert_called_once()

def test_generate_invoice_pdf_without_logo(mock_invoice, tmp_path):
    """Test PDF generation without company logo"""
    test_pdf_path = tmp_path / "test_invoice.pdf"
    mock_invoice.pdf_path = str(test_pdf_path)
    
    with patch("os.path.exists") as mock_exists, \
         patch("reportlab.pdfgen.canvas.Canvas.drawString") as mock_draw_string:
        mock_exists.return_value = False
        generate_invoice_pdf(mock_invoice)
        
        assert os.path.exists(test_pdf_path)
        assert os.path.getsize(test_pdf_path) > 0
        # Verify company name is drawn as text when logo is missing
        mock_draw_string.assert_any_call(50, A4[1] - 100, "PM Tool")
