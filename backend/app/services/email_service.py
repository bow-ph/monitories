from typing import List, Optional
import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, 
    Disposition, Personalization, To, From, Content
)
from app.core.config import settings
from pathlib import Path

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(os.getenv("Sendgrid___DocuPlanAI"))
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachments: Optional[List[tuple]] = None,
        email_type: str = "email"
    ) -> bool:
        """Send email using SendGrid"""
        try:
            # Create message with proper structure using helper classes
            message = Mail()
            message.from_email = From(email=self.from_email, name=self.from_name)
            personalization = Personalization()
            personalization.add_to(To(email=to_email))
            message.add_personalization(personalization)
            message.subject = subject
            message.add_content(Content("text/html", html_content))

            # Handle attachments
            if attachments:
                for attachment_path, filename in attachments:
                    if not os.path.exists(attachment_path):
                        print(f"Warning: Attachment file not found: {attachment_path}")
                        continue

                    try:
                        with open(attachment_path, 'rb') as f:
                            file_content = base64.b64encode(f.read()).decode()
                            attachment = Attachment()
                            attachment.file_content = FileContent(file_content)
                            attachment.file_type = FileType('application/pdf')
                            attachment.file_name = FileName(filename)
                            attachment.disposition = Disposition('attachment')
                            message.add_attachment(attachment)
                    except Exception as e:
                        print(f"Failed to attach file {filename}: {str(e)}")
                        continue

            # Send email
            self.client.send(message)
            return True
        except Exception as e:
            error_msg = f"Failed to send {email_type} email to {to_email}: {str(e)}"
            print(error_msg)
            return False

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email after registration"""
        subject = "Willkommen bei DocuPlanAI"
        content = f"""
        <h2>Willkommen bei DocuPlanAI!</h2>
        <p>Sehr geehrte(r) {username},</p>
        <p>vielen Dank für Ihre Registrierung bei DocuPlanAI. Wir freuen uns, Sie bei der effizienten Verwaltung Ihrer Projekte unterstützen zu dürfen.</p>
        <p>Sie können jetzt:</p>
        <ul>
            <li>Projekte erstellen und verwalten</li>
            <li>PDFs für die automatische Aufgabenextraktion hochladen</li>
            <li>Ihre Aufgaben mit Ihrem Kalender synchronisieren</li>
        </ul>
        <p>Bei Fragen stehen wir Ihnen gerne zur Verfügung.</p>
        <p>Mit freundlichen Grüßen<br>Ihr DocuPlanAI Team</p>
        """
        try:
            return self.send_email(to_email, subject, content, email_type="welcome")
        except Exception as e:
            print(f"Failed to send welcome email to {to_email}: {str(e)}")
            return False

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"https://docuplanai.com/reset-password?token={reset_token}"
        subject = "DocuPlanAI Passwort zurücksetzen"
        content = f"""
        <h2>Passwort zurücksetzen</h2>
        <p>Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts gestellt. Klicken Sie auf den folgenden Link, um fortzufahren:</p>
        <p><a href="{reset_url}">Passwort zurücksetzen</a></p>
        <p>Falls Sie keine Anfrage gestellt haben, können Sie diese E-Mail ignorieren.</p>
        <p>Mit freundlichen Grüßen<br>Ihr DocuPlanAI Team</p>
        """
        try:
            return self.send_email(to_email, subject, content, email_type="password reset")
        except Exception as e:
            print(f"Failed to send password reset email to {to_email}: {str(e)}")
            return False

    def send_payment_confirmation(
        self,
        to_email: str,
        package_name: str,
        amount: float,
        invoice_path: str
    ) -> bool:
        """Send payment confirmation with invoice"""
        subject = f"Zahlungsbestätigung - {package_name}"
        content = f"""
        <h2>Zahlungsbestätigung</h2>
        <p>Vielen Dank für Ihre Zahlung von €{amount:.2f} für das {package_name} Paket.</p>
        <p>Ihr Abonnement wurde aktiviert. Die Rechnung finden Sie im Anhang dieser E-Mail.</p>
        <p>Sie können Ihre Rechnungen auch jederzeit in Ihrem Kundenkonto unter <a href="https://docuplanai.com/account">https://docuplanai.com/account</a> einsehen.</p>
        <p>Mit freundlichen Grüßen<br>Ihr DocuPlanAI Team</p>
        """
        try:
            if not invoice_path or not os.path.exists(invoice_path):
                print(f"Invoice file not found at {invoice_path}")
                return self.send_email(to_email, subject, content, email_type="payment confirmation")
                
            attachments = [(invoice_path, f"rechnung_{package_name.lower().replace(' ', '_')}.pdf")]
            return self.send_email(to_email, subject, content, attachments, email_type="payment confirmation")
        except Exception as e:
            print(f"Failed to send payment confirmation to {to_email}: {str(e)}")
            return False

    def send_subscription_expiry_notice(self, to_email: str, days_left: int) -> bool:
        """Send subscription expiry notice"""
        subject = "Ablauf des Abonnements"
        content = f"""
        <h2>Hinweis zum Ablauf des Abonnements</h2>
        <p>Ihr DocuPlanAI Abonnement läuft in {days_left} Tagen ab.</p>
        <p>Um eine unterbrechungsfreie Nutzung zu gewährleisten, erneuern Sie bitte Ihr Abonnement.</p>
        <p><a href="https://docuplanai.com/subscription">Abonnement verlängern</a></p>
        <p>Mit freundlichen Grüßen<br>Ihr DocuPlanAI Team</p>
        """
        try:
            return self.send_email(to_email, subject, content, email_type="subscription expiry notice")
        except Exception as e:
            print(f"Failed to send subscription expiry notice to {to_email}: {str(e)}")
            return False

    def send_subscription_cancellation(self, to_email: str, package_name: str) -> bool:
        """Send subscription cancellation confirmation"""
        subject = "Bestätigung der Abonnement-Kündigung"
        content = f"""
        <h2>Bestätigung der Abonnement-Kündigung</h2>
        <p>Sehr geehrter Kunde,</p>
        <p>wir bestätigen hiermit die Kündigung Ihres Abonnements für das Paket "{package_name}".</p>
        <p>Ihr Zugang bleibt bis zum Ende der aktuellen Abrechnungsperiode aktiv.</p>
        <p>Wir bedauern, dass Sie uns verlassen. Falls Sie Feedback haben, wie wir unseren Service verbessern können, antworten Sie gerne auf diese E-Mail.</p>
        <p>Mit freundlichen Grüßen<br>Ihr DocuPlanAI Team</p>
        """
        try:
            return self.send_email(to_email, subject, content, email_type="subscription cancellation")
        except Exception as e:
            print(f"Failed to send subscription cancellation email to {to_email}: {str(e)}")
            return False
