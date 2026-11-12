
"""
Email Notification Service for PM-POSHAN Smart-Nourish System.
Sends OTP authentication codes through SMTP.
Development OTP previews are enabled only in development mode.
"""

import os
import smtplib
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure environment variables are loaded from .env
load_dotenv()

# Development-only OTP preview store
LATEST_DEV_OTPS = {}

def get_smtp_settings():
    load_dotenv()
    user = os.getenv("SMTP_USER", "").strip()
    return {
        "host": os.getenv("SMTP_HOST", "").strip(),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": user,
        "pass": os.getenv("SMTP_PASS", "").strip(),
        "from": (os.getenv("SMTP_FROM") or user).strip(),
        "env": os.getenv("APP_ENV", "production").lower()
    }


def send_otp_email(
    email: str,
    otp_code: str,
    recipient_name: str = "Educator"
) -> dict:
    """
    Send a 6-digit OTP through SMTP.

    Development:
        If SMTP is not configured or sending fails, return a
        development-only OTP preview.

    Production:
        Never expose the OTP. SMTP errors return success=False.
    """

    clean_email = email.strip().lower()
    safe_name = html.escape(recipient_name or "Educator")
    timestamp = datetime.now(timezone.utc).isoformat()

    cfg = get_smtp_settings()
    smtp_host = cfg["host"]
    smtp_port = cfg["port"]
    smtp_user = cfg["user"]
    smtp_pass = cfg["pass"]
    smtp_from = cfg["from"]
    is_development = cfg["env"] == "development"

    # SMTP configuration must be complete.
    smtp_configured = bool(smtp_host and smtp_user and smtp_pass and smtp_from)

    if not smtp_configured:
        message = "SMTP configuration is incomplete."

        if is_development:
            print(f"[DEV OTP] OTP for {clean_email}: {otp_code}")

            LATEST_DEV_OTPS[clean_email] = {
                "email": clean_email,
                "otp": otp_code,
                "recipient_name": recipient_name,
                "timestamp": timestamp
            }

            return {
                "success": True,
                "mode": "dev_simulator",
                "otp": otp_code,
                "email": clean_email,
                "timestamp": timestamp
            }

        print(f"[OTP ERROR] {message}")

        return {
            "success": False,
            "mode": "smtp_not_configured",
            "email": clean_email,
            "error": message
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Karnataka PM-POSHAN Verification Code"
        msg["From"] = smtp_from
        msg["To"] = clean_email

        text_content = f"""Namaste {recipient_name},

Your verification OTP code for Karnataka PM-POSHAN
(Smart-Nourish & Attend) is:

{otp_code}

This code expires in 5 minutes.
Do not share this code with anyone.

Department of School Education & Literacy,
Government of Karnataka
"""

        html_content = f"""
        <div style="font-family: Arial, sans-serif;
                    max-width: 500px; margin: auto; padding: 20px;
                    border: 1px solid #e0f2fe; border-radius: 12px;">

            <h2 style="color: #0284c7;">
                PM-POSHAN Portal Verification
            </h2>

            <p>Namaste <strong>{safe_name}</strong>,</p>

            <p>Your one-time authentication code is:</p>

            <div style="font-size: 28px; font-weight: bold;
                        letter-spacing: 4px; color: #0369a1;
                        background: #f0f9ff; padding: 12px;
                        border-radius: 8px; text-align: center;
                        margin: 16px 0;">
                {otp_code}
            </div>

            <p style="color: #64748b; font-size: 13px;">
                This code is valid for 5 minutes.
                If you did not request this code, ignore this email.
            </p>

            <hr style="border: none;
                       border-top: 1px solid #e2e8f0;
                       margin: 20px 0;" />

            <p style="color: #94a3b8; font-size: 11px;">
                Department of School Education and Literacy,
                Government of Karnataka
            </p>
        </div>
        """

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Port 465 uses SSL; other configured ports use STARTTLS.
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(
                smtp_host,
                smtp_port,
                timeout=15
            )
        else:
            server = smtplib.SMTP(
                smtp_host,
                smtp_port,
                timeout=15
            )
            server.ehlo()
            server.starttls()
            server.ehlo()

        try:
            server.login(smtp_user, smtp_pass)
            server.sendmail(
                smtp_from,
                [clean_email],
                msg.as_string()
            )
        finally:
            server.quit()

        print(f"[OTP EMAIL] Successfully sent to {clean_email} via {smtp_host}:{smtp_port}")

        # Do not return the OTP after successful SMTP delivery.
        return {
            "success": True,
            "mode": "smtp",
            "email": clean_email,
            "timestamp": timestamp
        }

    except Exception as e:
        print(f"[OTP SMTP ERROR] Failed to send to {clean_email}: {e}")

        # Development-only fallback.
        if is_development:
            LATEST_DEV_OTPS[clean_email] = {
                "email": clean_email,
                "otp": otp_code,
                "recipient_name": recipient_name,
                "timestamp": timestamp
            }

            return {
                "success": True,
                "mode": "dev_fallback",
                "otp": otp_code,
                "email": clean_email,
                "error": str(e)
            }

        # Production must never expose an OTP on SMTP failure.
        return {
            "success": False,
            "mode": "smtp_failed",
            "email": clean_email,
            "error": "Unable to deliver verification email."
        }


def send_password_reset_email(
    email: str,
    otp_code: str,
    recipient_name: str = "Head Master"
) -> dict:
    """Send a 6-digit password reset verification code via SMTP."""
    clean_email = email.strip().lower()
    safe_name = html.escape(recipient_name or "Head Master")
    timestamp = datetime.now(timezone.utc).isoformat()

    cfg = get_smtp_settings()
    smtp_host = cfg["host"]
    smtp_port = cfg["port"]
    smtp_user = cfg["user"]
    smtp_pass = cfg["pass"]
    smtp_from = cfg["from"]
    is_development = cfg["env"] == "development"

    smtp_configured = bool(smtp_host and smtp_user and smtp_pass and smtp_from)

    if not smtp_configured:
        if is_development:
            print(f"[DEV RESET OTP] Password reset OTP for {clean_email}: {otp_code}")
            LATEST_DEV_OTPS[clean_email] = {
                "email": clean_email,
                "otp": otp_code,
                "purpose": "password_reset",
                "recipient_name": recipient_name,
                "timestamp": timestamp
            }
            return {
                "success": True,
                "mode": "dev_simulator",
                "otp": otp_code,
                "email": clean_email,
                "timestamp": timestamp
            }
        return {
            "success": False,
            "mode": "smtp_not_configured",
            "email": clean_email,
            "error": "SMTP configuration is incomplete."
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Karnataka PM-POSHAN - Password Reset Verification Code"
        msg["From"] = smtp_from
        msg["To"] = clean_email

        text_content = f"""Namaste {recipient_name},

You have requested to reset the administrative password for your Karnataka PM-POSHAN (Akshara Dasoha) account.

Your Password Reset Verification OTP is:
{otp_code}

This code will expire in 5 minutes.
If you did not request this password reset, please ignore this email or contact system administration.

Department of School Education & Literacy,
Government of Karnataka
"""

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 20px; border: 1px solid #e0f2fe; border-radius: 12px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <h2 style="color: #0284c7; margin: 0;">PM-POSHAN Password Reset</h2>
            </div>
            <p>Namaste <strong>{safe_name}</strong>,</p>
            <p>You have requested to reset the password for your Karnataka PM-POSHAN administrative account.</p>
            <p>Your one-time password reset code is:</p>
            <div style="font-size: 30px; font-weight: bold; letter-spacing: 5px; color: #0284c7; background: #f0f9ff; padding: 14px; border-radius: 8px; text-align: center; margin: 16px 0; border: 1px dashed #38bdf8;">
                {otp_code}
            </div>
            <p style="color: #64748b; font-size: 13px;">
                This code is valid for <strong>5 minutes</strong>. If you did not initiate this request, your account remains secure and you can safely ignore this email.
            </p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
            <p style="color: #94a3b8; font-size: 11px;">
                Department of School Education and Literacy, Government of Karnataka
            </p>
        </div>
        """

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()

        try:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [clean_email], msg.as_string())
        finally:
            server.quit()

        print(f"[RESET OTP EMAIL] Successfully sent password reset code to {clean_email}")
        return {
            "success": True,
            "mode": "smtp",
            "email": clean_email,
            "timestamp": timestamp
        }

    except Exception as e:
        print(f"[RESET OTP ERROR] Failed to send to {clean_email}: {e}")
        if is_development:
            LATEST_DEV_OTPS[clean_email] = {
                "email": clean_email,
                "otp": otp_code,
                "purpose": "password_reset",
                "recipient_name": recipient_name,
                "timestamp": timestamp
            }
            return {
                "success": True,
                "mode": "dev_fallback",
                "otp": otp_code,
                "email": clean_email,
                "error": str(e)
            }
        return {
            "success": False,
            "mode": "smtp_failed",
            "email": clean_email,
            "error": "Unable to deliver password reset email."
        }
