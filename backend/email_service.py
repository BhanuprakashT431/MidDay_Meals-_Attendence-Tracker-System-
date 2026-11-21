"""
Email Notification Service for PM-POSHAN Smart-Nourish System.
Supports:
1. HTTPS REST API (Brevo / Sendinblue) - Port 443 (Recommended for Render Free Tier)
2. HTTPS REST API (Resend) - Port 443
3. Standard SMTP (Gmail / Custom) - Port 587 / 465 (Works on VPS, Koyeb, Local)
4. Cloud Firewall Fallback: If cloud host firewall (e.g. Render Free Tier) blocks SMTP ports 25/465/587,
   gracefully delivers a fallback OTP so users are never locked out of the system.
"""

import os
import socket
import smtplib
import html
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure environment variables are loaded from .env
load_dotenv()

# Development & Fallback OTP preview store
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
        "env": os.getenv("APP_ENV", "production").lower(),
        "brevo_api_key": os.getenv("BREVO_API_KEY", "").strip(),
        "resend_api_key": os.getenv("RESEND_API_KEY", "").strip(),
        "allow_fallback": os.getenv("ALLOW_FALLBACK_OTP", "true").lower() in ("true", "1", "yes")
    }


def send_via_brevo_api(api_key: str, to_email: str, recipient_name: str, subject: str, text_content: str, html_content: str, from_email: str) -> bool:
    """Send transactional email via Brevo (Sendinblue) REST API over HTTPS (port 443)."""
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        sender_email = from_email or "noreply@karnataka.gov.in"
        payload = {
            "sender": {"name": "Karnataka PM-POSHAN", "email": sender_email},
            "to": [{"email": to_email, "name": recipient_name}],
            "subject": subject,
            "htmlContent": html_content,
            "textContent": text_content
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code in (200, 201, 202):
            print(f"[BREVO API EMAIL] Successfully sent email to {to_email} via Brevo HTTPS API")
            return True
        else:
            print(f"[BREVO API ERROR] Status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[BREVO API EXCEPTION] {e}")
        return False


def send_via_resend_api(api_key: str, to_email: str, recipient_name: str, subject: str, text_content: str, html_content: str, from_email: str) -> bool:
    """Send transactional email via Resend REST API over HTTPS (port 443)."""
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        sender_email = from_email or "onboarding@resend.dev"
        payload = {
            "from": f"Karnataka PM-POSHAN <{sender_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code in (200, 201, 202):
            print(f"[RESEND API EMAIL] Successfully sent email to {to_email} via Resend HTTPS API")
            return True
        else:
            print(f"[RESEND API ERROR] Status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[RESEND API EXCEPTION] {e}")
        return False


def send_otp_email(
    email: str,
    otp_code: str,
    recipient_name: str = "Educator"
) -> dict:
    """
    Send a 6-digit OTP through HTTPS API or SMTP, with graceful cloud firewall fallback.
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
    allow_fallback = cfg["allow_fallback"]

    subject = "Karnataka PM-POSHAN Verification Code"
    text_content = f"""Namaste {recipient_name},

Your verification OTP code for Karnataka PM-POSHAN (Smart-Nourish & Attend) is:

{otp_code}

This code expires in 5 minutes.
Do not share this code with anyone.

Department of School Education & Literacy,
Government of Karnataka
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 20px; border: 1px solid #e0f2fe; border-radius: 12px;">
        <h2 style="color: #0284c7;">PM-POSHAN Portal Verification</h2>
        <p>Namaste <strong>{safe_name}</strong>,</p>
        <p>Your one-time authentication code is:</p>
        <div style="font-size: 28px; font-weight: bold; letter-spacing: 4px; color: #0369a1; background: #f0f9ff; padding: 12px; border-radius: 8px; text-align: center; margin: 16px 0;">
            {otp_code}
        </div>
        <p style="color: #64748b; font-size: 13px;">This code is valid for 5 minutes. If you did not request this code, ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
        <p style="color: #94a3b8; font-size: 11px;">Department of School Education and Literacy, Government of Karnataka</p>
    </div>
    """

    # 1. PRIORITY 1: Brevo HTTPS REST API (Port 443 - Never blocked on Render Free)
    if cfg["brevo_api_key"]:
        if send_via_brevo_api(cfg["brevo_api_key"], clean_email, recipient_name, subject, text_content, html_content, smtp_from):
            return {"success": True, "mode": "brevo_https", "email": clean_email, "timestamp": timestamp}

    # 2. PRIORITY 2: Resend HTTPS REST API (Port 443 - Never blocked on Render Free)
    if cfg["resend_api_key"]:
        if send_via_resend_api(cfg["resend_api_key"], clean_email, recipient_name, subject, text_content, html_content, smtp_from):
            return {"success": True, "mode": "resend_https", "email": clean_email, "timestamp": timestamp}

    # 3. PRIORITY 3: Traditional SMTP (Gmail / Custom)
    smtp_configured = bool(smtp_host and smtp_user and smtp_pass and smtp_from)
    if smtp_configured:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_from
            msg["To"] = clean_email
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Short 6-second timeout to quickly catch cloud provider port drops
            if smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=6)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=6)
                server.ehlo()
                server.starttls()
                server.ehlo()

            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [clean_email], msg.as_string())
            server.quit()

            print(f"[OTP EMAIL] Successfully sent to {clean_email} via {smtp_host}:{smtp_port}")
            return {"success": True, "mode": "smtp", "email": clean_email, "timestamp": timestamp}

        except Exception as e:
            print(f"[OTP SMTP WARNING] Outbound SMTP to {smtp_host}:{smtp_port} failed ({e}). "
                  f"Note: Hosting providers like Render Free Tier drop traditional SMTP traffic on ports 25, 465, and 587.")

    # 4. GRACEFUL CLOUD FIREWALL / DEV FALLBACK
    # Never leave the user stuck on 500 error if the host firewall blocks SMTP
    if is_development or allow_fallback or not smtp_configured:
        print(f"[FALLBACK OTP ACTIVE] Dispatched fallback OTP for {clean_email}: {otp_code}")
        LATEST_DEV_OTPS[clean_email] = {
            "email": clean_email,
            "otp": otp_code,
            "recipient_name": recipient_name,
            "timestamp": timestamp
        }
        return {
            "success": True,
            "mode": "cloud_firewall_fallback",
            "otp": otp_code,
            "email": clean_email,
            "timestamp": timestamp
        }

    return {
        "success": False,
        "mode": "smtp_failed",
        "email": clean_email,
        "error": "Outbound email blocked by cloud firewall. Add BREVO_API_KEY or set ALLOW_FALLBACK_OTP=true in Render environment."
    }


def send_password_reset_email(
    email: str,
    otp_code: str,
    recipient_name: str = "Head Master"
) -> dict:
    """Send a 6-digit password reset verification code via HTTPS API or SMTP."""
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
    allow_fallback = cfg["allow_fallback"]

    subject = "Karnataka PM-POSHAN - Password Reset Verification Code"
    text_content = f"""Namaste {recipient_name},

You have requested to reset the administrative password for your Karnataka PM-POSHAN account.

Your Password Reset Verification OTP is:
{otp_code}

This code will expire in 5 minutes.
If you did not request this password reset, please ignore this email.

Department of School Education & Literacy,
Government of Karnataka
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 20px; border: 1px solid #e0f2fe; border-radius: 12px;">
        <h2 style="color: #0284c7; margin: 0;">PM-POSHAN Password Reset</h2>
        <p>Namaste <strong>{safe_name}</strong>,</p>
        <p>Your one-time password reset code is:</p>
        <div style="font-size: 30px; font-weight: bold; letter-spacing: 5px; color: #0284c7; background: #f0f9ff; padding: 14px; border-radius: 8px; text-align: center; margin: 16px 0; border: 1px dashed #38bdf8;">
            {otp_code}
        </div>
        <p style="color: #64748b; font-size: 13px;">This code is valid for 5 minutes. If you did not initiate this request, safely ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
        <p style="color: #94a3b8; font-size: 11px;">Department of School Education and Literacy, Government of Karnataka</p>
    </div>
    """

    # 1. Brevo HTTPS API
    if cfg["brevo_api_key"]:
        if send_via_brevo_api(cfg["brevo_api_key"], clean_email, recipient_name, subject, text_content, html_content, smtp_from):
            return {"success": True, "mode": "brevo_https", "email": clean_email, "timestamp": timestamp}

    # 2. Resend HTTPS API
    if cfg["resend_api_key"]:
        if send_via_resend_api(cfg["resend_api_key"], clean_email, recipient_name, subject, text_content, html_content, smtp_from):
            return {"success": True, "mode": "resend_https", "email": clean_email, "timestamp": timestamp}

    # 3. Traditional SMTP
    smtp_configured = bool(smtp_host and smtp_user and smtp_pass and smtp_from)
    if smtp_configured:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_from
            msg["To"] = clean_email
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            if smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=6)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=6)
                server.ehlo()
                server.starttls()
                server.ehlo()

            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [clean_email], msg.as_string())
            server.quit()

            print(f"[RESET OTP EMAIL] Successfully sent password reset code to {clean_email}")
            return {"success": True, "mode": "smtp", "email": clean_email, "timestamp": timestamp}

        except Exception as e:
            print(f"[RESET OTP WARNING] Outbound SMTP failed ({e}). Note: Render Free drops outbound SMTP ports 25, 465, 587.")

    # 4. Fallback
    if is_development or allow_fallback or not smtp_configured:
        print(f"[FALLBACK RESET OTP ACTIVE] Dispatched fallback password reset OTP for {clean_email}: {otp_code}")
        LATEST_DEV_OTPS[clean_email] = {
            "email": clean_email,
            "otp": otp_code,
            "purpose": "password_reset",
            "recipient_name": recipient_name,
            "timestamp": timestamp
        }
        return {
            "success": True,
            "mode": "cloud_firewall_fallback",
            "otp": otp_code,
            "email": clean_email,
            "timestamp": timestamp
        }

    return {
        "success": False,
        "mode": "smtp_failed",
        "email": clean_email,
        "error": "Outbound email blocked by cloud firewall. Add BREVO_API_KEY or set ALLOW_FALLBACK_OTP=true in Render environment."
    }
