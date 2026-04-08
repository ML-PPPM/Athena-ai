#!/usr/bin/env python3
"""Test script for email verification functionality."""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_verification import email_verifier
from config import settings

def test_email_verification():
    """Test email verification functionality."""
    print("🧪 Testing Email Verification Functionality")
    print("=" * 50)

    # Check configuration
    print(f"Email verification enabled: {email_verifier.enabled}")
    print(f"SMTP Server: {email_verifier.smtp_server}")
    print(f"SMTP Port: {email_verifier.smtp_port}")
    print(f"SMTP Username configured: {bool(email_verifier.username)}")
    print(f"SMTP Password configured: {bool(email_verifier.password)}")
    print(f"From Email: {email_verifier.from_email}")
    print()

    if not email_verifier.enabled:
        print("❌ Email verification is disabled")
        return

    if not email_verifier.username or not email_verifier.password:
        print("❌ SMTP credentials not configured")
        print("Please set SMTP_USERNAME and SMTP_PASSWORD in your .env file")
        return

    # Test email sending
    test_email = input("Enter a test email address to send verification code to: ").strip()
    if not test_email:
        print("❌ No email provided")
        return

    print(f"📧 Sending verification code to: {test_email}")

    code = email_verifier.send_verification_code(test_email)
    if code:
        print(f"✅ Verification code sent successfully!")
        print(f"📝 Code: {code} (for testing purposes)")
        print("Check your email for the verification message.")
    else:
        print("❌ Failed to send verification email")
        print("Check your SMTP configuration and try again.")

if __name__ == "__main__":
    test_email_verification()