"""Email verification functionality for Athena AI."""
import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import logging
from config import settings

logger = logging.getLogger(__name__)

class EmailVerifier:
    """Handles email verification through SMTP."""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.enabled = settings.EMAIL_VERIFICATION_ENABLED

    def generate_verification_code(self, length: int = 6) -> str:
        """Generate a random verification code."""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def send_verification_email(self, to_email: str, verification_code: str) -> bool:
        """Send verification email with code."""
        if not self.enabled or not self.username or not self.password:
            logger.warning("Email verification is disabled or not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email or self.username
            msg['To'] = to_email
            msg['Subject'] = "Athena AI - Email Verification Code"

            body = f"""
            Welcome to Athena AI!

            Your verification code is: {verification_code}

            Please enter this code in the app to verify your email address.

            If you didn't request this verification, please ignore this email.

            Best regards,
            Athena AI Team
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email or self.username, to_email, text)
            server.quit()

            logger.info(f"Verification email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send verification email to {to_email}: {e}")
            return False

    def send_verification_code(self, to_email: str) -> Optional[str]:
        """Generate and send verification code, return the code for storage."""
        if not self.enabled:
            logger.info("Email verification disabled, skipping")
            return None

        verification_code = self.generate_verification_code()

        if self.send_verification_email(to_email, verification_code):
            return verification_code
        else:
            return None

# Global email verifier instance
email_verifier = EmailVerifier()