import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Tuple
import httpx

from backend.app.core.config import settings

logger = logging.getLogger("gaadilelo.email")

class EmailService:
    """
    Transactional email service for GaadiLelo.com.
    Supports SMTP, SendGrid, and a local Mock provider.
    Mock provider is strictly blocked in production.
    """

    @classmethod
    async def send_verification_email(
        cls,
        to_email: str,
        token: str,
        user_name: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        subject = "Verify your email address — GaadiLelo"
        name = user_name or "Vehicle Buyer"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background: #f8fafc; padding: 24px; color: #1e293b;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; padding: 32px; border: 1px solid #e2e8f0;">
                <h2 style="color: #0f172a; margin-top: 0;">Welcome to GaadiLelo</h2>
                <p>Hello {name},</p>
                <p>Thank you for joining GaadiLelo, India's premier vehicle group-buying platform. Please confirm your email address to activate your account:</p>
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{verification_link}" style="background-color: #2563eb; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Verify Email Address</a>
                </div>
                <p style="font-size: 13px; color: #64748b;">This link will expire in 48 hours and can only be used once. If you did not create an account on GaadiLelo, you can safely ignore this email.</p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
                <p style="font-size: 12px; color: #94a3b8; text-align: center;">GaadiLelo — Buy Together. Save Together. Indore, MP, India.</p>
            </div>
        </body>
        </html>
        """
        return await cls._dispatch(to_email=to_email, subject=subject, html_body=html_content)

    @classmethod
    async def send_password_reset_email(
        cls,
        to_email: str,
        token: str,
        user_name: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Reset your password — GaadiLelo"
        name = user_name or "GaadiLelo User"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background: #f8fafc; padding: 24px; color: #1e293b;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; padding: 32px; border: 1px solid #e2e8f0;">
                <h2 style="color: #0f172a; margin-top: 0;">Password Reset Request</h2>
                <p>Hello {name},</p>
                <p>We received a request to reset the password for your GaadiLelo account. Click the button below to choose a new password:</p>
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{reset_link}" style="background-color: #dc2626; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Reset Password</a>
                </div>
                <p style="font-size: 13px; color: #64748b;">This link will expire in 1 hour and can only be used once. If you did not request a password reset, please contact support or ignore this message.</p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
                <p style="font-size: 12px; color: #94a3b8; text-align: center;">GaadiLelo Security Desk — Indore, MP, India.</p>
            </div>
        </body>
        </html>
        """
        return await cls._dispatch(to_email=to_email, subject=subject, html_body=html_content)

    @classmethod
    async def _dispatch(cls, to_email: str, subject: str, html_body: str) -> Tuple[bool, Optional[str]]:
        provider = (settings.EMAIL_PROVIDER or "mock").lower()

        # Reject mock email in production
        if settings.ENVIRONMENT.lower() == "production" and provider == "mock":
            err_msg = "Mock email provider is rejected in production mode. Configure SMTP or SendGrid."
            logger.error(err_msg)
            return False, err_msg

        if provider == "mock":
            logger.info(f"[MOCK EMAIL] Dispatch to={to_email} subject='{subject}'")
            return True, None

        elif provider == "smtp":
            if not settings.SMTP_HOST:
                err_msg = "SMTP_HOST is not configured."
                logger.error(err_msg)
                return False, err_msg
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = settings.SMTP_FROM_EMAIL
                msg["To"] = to_email
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                    if settings.SMTP_USE_TLS:
                        server.starttls()
                    if settings.SMTP_USER and settings.SMTP_PASSWORD:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)
                logger.info(f"Email successfully sent via SMTP to {to_email}")
                return True, None
            except Exception as e:
                err_msg = f"SMTP dispatch failed: {str(e)}"
                logger.error(err_msg)
                return False, err_msg

        elif provider == "sendgrid":
            if not settings.SENDGRID_API_KEY:
                err_msg = "SENDGRID_API_KEY is not configured."
                logger.error(err_msg)
                return False, err_msg
            try:
                payload = {
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": settings.SENDGRID_FROM_EMAIL, "name": "GaadiLelo"},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": html_body}]
                }
                headers = {
                    "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                    "Content-Type": "application/json"
                }
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers)
                    if resp.status_code in [200, 201, 202]:
                        logger.info(f"Email successfully dispatched via SendGrid to {to_email}")
                        return True, None
                    else:
                        err_msg = f"SendGrid API returned status {resp.status_code}: {resp.text}"
                        logger.error(err_msg)
                        return False, err_msg
            except Exception as e:
                err_msg = f"SendGrid dispatch failed: {str(e)}"
                logger.error(err_msg)
                return False, err_msg

        else:
            err_msg = f"Unknown EMAIL_PROVIDER: {provider}"
            logger.error(err_msg)
            return False, err_msg

