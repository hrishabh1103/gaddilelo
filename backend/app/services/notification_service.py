import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.models import Notification
from backend.app.core.config import settings

logger = logging.getLogger("gaadilelo.notifications")

class NotificationService:
    """
    Extensible notification engine. Persists in-app notifications to database,
    and exposes structured hooks for SMS (Twilio/Kaleyra/MSG91), Email (Resend/SendGrid),
    and WhatsApp Business API.
    """

    @classmethod
    async def notify(
        cls,
        db: AsyncSession,
        user_id: str,
        title: str,
        message: str,
        event_type: str,
        link_url: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        recipient_email: Optional[str] = None
    ) -> Notification:
        # 1. Primary: In-App Notification (Always persistent)
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            event_type=event_type,
            link_url=link_url,
            is_read=False
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        # 2. Extensible SMS Dispatch (Configurable)
        if settings.SMS_PROVIDER != "mock" and recipient_phone:
            cls._dispatch_sms(recipient_phone, message)
        else:
            logger.info(f"[SMS MOCK] To {recipient_phone or user_id}: {message}")

        # 3. Extensible Email Dispatch (Configurable)
        if settings.EMAIL_PROVIDER != "mock" and recipient_email:
            cls._dispatch_email(recipient_email, title, message)
        else:
            logger.info(f"[EMAIL MOCK] To {recipient_email or user_id}: {title} - {message}")

        # 4. WhatsApp Business API Hook
        if settings.WHATSAPP_ENABLED and recipient_phone:
            cls._dispatch_whatsapp(recipient_phone, message)

        return notification

    @staticmethod
    def _dispatch_sms(phone: str, text: str):
        # Ready for live integration (e.g. MSG91, Kaleyra, Twilio)
        logger.info(f"[SMS LIVE HOOK] Configured provider '{settings.SMS_PROVIDER}' invoked for {phone}")

    @staticmethod
    def _dispatch_email(email: str, subject: str, body: str):
        # Ready for live integration (e.g. Resend, Sendgrid, SMTP)
        logger.info(f"[EMAIL LIVE HOOK] Configured provider '{settings.EMAIL_PROVIDER}' invoked for {email}")

    @staticmethod
    def _dispatch_whatsapp(phone: str, body: str):
        # Ready for live integration (Meta Cloud WhatsApp API)
        logger.info(f"[WHATSAPP LIVE HOOK] Dispatching to {phone}")
