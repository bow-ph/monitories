import pytest
import base64
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition
)

@pytest.fixture
def email_service():
    with patch.dict('os.environ', {
        'SENDGRID_API_KEY': 'test_key',
        'SMTP_FROM_EMAIL': 'test@example.com',
        'SMTP_FROM_NAME': 'Test Sender'
    }):
        return EmailService()

def test_send_welcome_email(email_service):
    """Test sending welcome email in German"""
    with patch.object(email_service.client, 'send') as mock_send:
        mock_send.return_value = True  # Mock successful send
        result = email_service.send_welcome_email("test@example.com", "Max Mustermann")
        assert result is True
        
        # Verify email was sent with correct parameters
        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]
        assert isinstance(message, Mail)
        
        # Verify email structure
        assert message.from_email.email == email_service.from_email
        assert message.from_email.name == email_service.from_name
        assert len(message.personalizations) == 1
        assert message.personalizations[0].tos[0]["email"] == "test@example.com"
        assert message.subject.get() == "Willkommen bei DocuPlanAI"
        assert len(message.contents) == 1
        assert message.contents[0].mime_type == "text/html"
        assert "Sehr geehrte(r) Max Mustermann" in message.contents[0].content
        assert "Projekte erstellen und verwalten" in message.contents[0].content
        assert "Mit freundlichen Grüßen" in message.contents[0].content
        assert "DocuPlanAI Team" in message.contents[0].content

def test_send_password_reset_email(email_service):
    """Test sending password reset email in German"""
    with patch.object(email_service.client, 'send') as mock_send:
        mock_send.return_value = True  # Mock successful send
        result = email_service.send_password_reset_email("test@example.com", "test-token")
        assert result is True
        
        # Verify email was sent with correct parameters
        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]
        assert isinstance(message, Mail)
        
        # Verify email structure
        assert message.from_email.email == email_service.from_email
        assert message.from_email.name == email_service.from_name
        assert len(message.personalizations) == 1
        assert message.personalizations[0].tos[0]["email"] == "test@example.com"
        assert message.subject.get() == "DocuPlanAI Passwort zurücksetzen"
        assert len(message.contents) == 1
        assert message.contents[0].mime_type == "text/html"
        assert "Passwort zurücksetzen" in message.contents[0].content
        assert "test-token" in message.contents[0].content
        assert "Mit freundlichen Grüßen" in message.contents[0].content
        assert "DocuPlanAI Team" in message.contents[0].content
        assert "https://docuplanai.com/reset-password?token=test-token" in message.contents[0].content

def test_send_payment_confirmation(email_service):
    """Test sending payment confirmation email in German"""
    mock_file_content = b"test content"
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = mock_file_content
    
    with patch.object(email_service.client, 'send') as mock_send, \
         patch('builtins.open', return_value=mock_file), \
         patch('os.path.exists', return_value=True):
        mock_send.return_value = True  # Mock successful send
        result = email_service.send_payment_confirmation(
            "test@example.com",
            "Team Paket",
            99.99,
            "/tmp/test-invoice.pdf"
        )
        assert result is True
        
        # Verify email content
        call_args = mock_send.call_args[0][0]
        assert isinstance(call_args, Mail)
        
        # Verify basic email structure
        assert call_args.from_email.email == email_service.from_email
        assert call_args.from_email.name == email_service.from_name
        assert len(call_args.personalizations) == 1
        assert call_args.personalizations[0].tos[0]["email"] == "test@example.com"
        
        # Verify content
        content = call_args.contents[0]
        assert content.mime_type == "text/html"
        content_str = content.content
        assert "€99.99" in content_str
        assert "Ihr Abonnement wurde aktiviert" in content_str
        assert "https://docuplanai.com/account" in content_str
        
        # Verify attachment
        assert len(call_args.attachments) == 1
        attachment = call_args.attachments[0]
        # Verify attachment properties
        assert isinstance(attachment.file_name, FileName)
        assert isinstance(attachment.file_content, FileContent)
        assert isinstance(attachment.file_type, FileType)
        assert isinstance(attachment.disposition, Disposition)
        
        # Verify attachment values
        assert attachment.file_name.get() == "rechnung_team_paket.pdf"
        assert attachment.file_content.get() == base64.b64encode(mock_file_content).decode()
        assert attachment.file_type.get() == "application/pdf"
        assert attachment.disposition.get() == "attachment"

def test_send_subscription_expiry_notice(email_service):
    """Test sending subscription expiry notice in German"""
    with patch.object(email_service.client, 'send') as mock_send:
        mock_send.return_value = True  # Mock successful send
        result = email_service.send_subscription_expiry_notice("test@example.com", 7)
        assert result is True
        
        # Verify email was sent with correct parameters
        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]
        assert isinstance(message, Mail)
        
        # Verify email structure
        assert message.from_email.email == email_service.from_email
        assert message.from_email.name == email_service.from_name
        assert len(message.personalizations) == 1
        assert message.personalizations[0].tos[0]["email"] == "test@example.com"
        
        # Verify content
        assert len(message.contents) == 1
        assert message.contents[0].mime_type == "text/html"
        assert "7 Tagen" in message.contents[0].content
        assert "Abonnement verlängern" in message.contents[0].content
        assert "Mit freundlichen Grüßen" in message.contents[0].content
        assert "DocuPlanAI Team" in message.contents[0].content
        assert "https://docuplanai.com/subscription" in message.contents[0].content

def test_email_error_handling(email_service):
    """Test error handling in email sending"""
    test_error_msg = "Test error"
    test_email = "test@example.com"
    
    # Test welcome email error handling
    with patch.object(email_service.client, 'send', side_effect=Exception(test_error_msg)), \
         patch('builtins.print') as mock_print:
        result = email_service.send_welcome_email(test_email, "Test User")
        assert result is False
        mock_print.assert_called_with(f"Failed to send welcome email to {test_email}: {test_error_msg}")
    
    # Test password reset email error handling
    with patch.object(email_service.client, 'send', side_effect=Exception(test_error_msg)), \
         patch('builtins.print') as mock_print:
        result = email_service.send_password_reset_email(test_email, "test-token")
        assert result is False
        mock_print.assert_called_with(f"Failed to send password reset email to {test_email}: {test_error_msg}")
    
    # Test payment confirmation email error handling
    with patch.object(email_service.client, 'send', side_effect=Exception(test_error_msg)), \
         patch('builtins.print') as mock_print:
        result = email_service.send_payment_confirmation(test_email, "Test Package", 99.99, "/tmp/test.pdf")
        assert result is False
        mock_print.assert_called_with(f"Failed to send payment confirmation email to {test_email}: {test_error_msg}")
    
    # Test subscription expiry notice error handling
    with patch.object(email_service.client, 'send', side_effect=Exception(test_error_msg)), \
         patch('builtins.print') as mock_print:
        result = email_service.send_subscription_expiry_notice(test_email, 7)
        assert result is False
        mock_print.assert_called_with(f"Failed to send subscription expiry notice email to {test_email}: {test_error_msg}")
    
    # Test subscription cancellation email error handling
    with patch.object(email_service.client, 'send', side_effect=Exception(test_error_msg)), \
         patch('builtins.print') as mock_print:
        result = email_service.send_subscription_cancellation(test_email, "Test Package")
        assert result is False
        mock_print.assert_called_with(f"Failed to send subscription cancellation email to {test_email}: {test_error_msg}")

def test_attachment_handling(email_service):
    """Test handling of email attachments"""
    mock_file_content = b"test content"
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = mock_file_content
    
    with patch('builtins.open', return_value=mock_file), \
         patch('os.path.exists', return_value=True):
        with patch.object(email_service.client, 'send') as mock_send:
            result = email_service.send_payment_confirmation(
                "test@example.com",
                "Test Package",
                99.99,
                "/tmp/test-invoice.pdf"
            )
            assert result is True
            
            # Verify email was sent with correct parameters
            mock_send.assert_called_once()
            message = mock_send.call_args[0][0]
            assert isinstance(message, Mail)
            
            # Verify email structure
            assert message.from_email.email == email_service.from_email
            assert message.from_email.name == email_service.from_name
            assert len(message.personalizations) == 1
            assert message.personalizations[0].tos[0]["email"] == "test@example.com"
            
            # Verify content
            assert len(message.contents) == 1
            assert message.contents[0].mime_type == "text/html"
            assert message.subject.get() == "Zahlungsbestätigung - Test Package"
            assert "€99.99" in message.contents[0].content
            assert "Ihr Abonnement wurde aktiviert" in message.contents[0].content
            assert "Mit freundlichen Grüßen" in message.contents[0].content
            assert "DocuPlanAI Team" in message.contents[0].content
            
            # Verify attachment
            assert len(message.attachments) == 1
            attachment = message.attachments[0]
            # Verify attachment properties
            assert isinstance(attachment.file_name, FileName)
            assert isinstance(attachment.file_content, FileContent)
            assert isinstance(attachment.file_type, FileType)
            assert isinstance(attachment.disposition, Disposition)
            
            # Verify attachment values
            assert attachment.file_name.get() == "rechnung_test_package.pdf"
            assert attachment.file_content.get() == base64.b64encode(mock_file_content).decode()
            assert attachment.file_type.get() == "application/pdf"
            assert attachment.disposition.get() == "attachment"
