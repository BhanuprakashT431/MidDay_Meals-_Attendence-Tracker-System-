"""
Smart-Nourish & Attend: Digital Mid-Day Meal and Attendance Management System
Karnataka School PM-POSHAN (Akshara Dasoha) Tracking System
Main FastAPI Application & Secure Server
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()
import base64
from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from database import get_db_connection, init_db
from security import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_roles, generate_secure_otp,
    hash_otp, verify_otp_hash, MAX_OTP_ATTEMPTS, OTP_EXPIRE_MINUTES
)
from email_service import send_otp_email, send_password_reset_email, LATEST_DEV_OTPS
from firebase_config import (
    get_public_firebase_config, get_meta_config, get_stitch_config, update_runtime_keys,
    FIREBASE_CONFIG, META_CONFIG
)
from models import (
    UserLoginPassword, UserRequestOTP, UserVerifyOTP, UserRegister, SchoolSetup,
    FirebaseAuthPayload, MetaAuthPayload, ForgotPasswordRequest, ResetPasswordRequest,
    AttendanceItem, AttendanceSubmission, MealRecordCreate, StockInwardCreate,
    StockAdjustmentCreate, FreshProduceCreate, RuntimeKeysPayload, GeotagPhotoUpload
)

# Initialize database schema
init_db()

app = FastAPI(
    title="Smart-Nourish & Attend API",
    description="Backend API for Karnataka School Mid-Day Meal & Student Attendance Tracking System",
    version="1.0.0"
)

# Enable CORS for mobile apps, localhost, and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/") or request.url.path == "/" or request.url.path == "/sw.js":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

def record_audit(conn, school_id: int, user_id: Optional[int], user_name: Optional[str],
                 user_role: Optional[str], action: str, details: str, ip: str = "127.0.0.1"):
    """Helper to append an entry to the tamper-evident audit trail."""
    try:
        conn.execute("""
            INSERT INTO audit_logs (school_id, user_id, user_name, user_role, action, details, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (school_id, user_id, user_name, user_role, action, details, ip))
    except Exception as e:
        print(f"Error logging audit: {e}")

@app.get("/api/health", summary="Health Check API")
@app.get("/health", include_in_schema=False)
def health_check():
    return {
        "status": "healthy",
        "app": "Smart-Nourish & Attend (Karnataka PM-POSHAN)",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# ==========================================
# 1. AUTHENTICATION & SECURITY ENDPOINTS
# ==========================================

def create_and_send_auth_otp(conn, user, email: str, request: Request, purpose: str):
    """Create an OTP for one specific login flow and send it to the user's email."""
    recent_otp = conn.execute("""
        SELECT created_at FROM otp_codes
        WHERE LOWER(email) = ? AND purpose = ?
          AND created_at >= datetime('now', '-45 seconds')
        ORDER BY id DESC LIMIT 1
    """, (email, purpose)).fetchone()

    if recent_otp:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 45 seconds before requesting another verification OTP."
        )

    # Invalidate only previous OTPs belonging to this same authentication flow.
    conn.execute("""
        UPDATE otp_codes SET is_used = 1
        WHERE LOWER(email) = ? AND purpose = ? AND is_used = 0
    """, (email, purpose))

    otp_code = generate_secure_otp()
    hashed_otp = hash_otp(otp_code, email)
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    conn.execute("""
        INSERT INTO otp_codes (email, otp_hash, expires_at, purpose)
        VALUES (?, ?, ?, ?)
    """, (email, hashed_otp, expires_at, purpose))

    send_result = send_otp_email(email, otp_code, user["full_name"])
    if not send_result.get("success"):
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=send_result.get("error", "Failed to send verification OTP via email. Please verify SMTP settings.")
        )

    client_ip = request.client.host if request.client else "127.0.0.1"
    audit_action = "PASSWORD_OTP_REQUESTED" if purpose == "password_login" else "OTP_REQUESTED"
    record_audit(
        conn, user["school_id"], user["id"], user["full_name"], user["role"],
        audit_action, f"6-digit {purpose} OTP generated for {email}", client_ip
    )
    conn.commit()

    response = {
        "success": True,
        "message": f"Verification code sent to {email}. Please check your email inbox.",
        "expires_in_minutes": OTP_EXPIRE_MINUTES,
        "email": email
    }

    # Only include preview if running in developer simulator mode or cloud firewall fallback
    if send_result.get("mode") in ["dev_simulator", "dev_fallback", "cloud_firewall_fallback"]:
        response["dev_preview_otp"] = otp_code
        response["message"] += f" (Test OTP: {otp_code})"

    return response


def complete_otp_login(payload: UserVerifyOTP, request: Request, purpose: str):
    """Verify an OTP for the requested flow and issue a JWT only after success."""
    email = payload.email.strip().lower()
    input_otp = (payload.otp or payload.otp_code or "").strip()

    if len(input_otp) != 6 or not input_otp.isdigit():
        raise HTTPException(status_code=400, detail="Enter the valid 6-digit OTP.")

    conn = get_db_connection()
    user = conn.execute("""
        SELECT u.*, s.name as school_name, s.dise_code
        FROM users u
        LEFT JOIN schools s ON u.school_id = s.id
        WHERE LOWER(u.email) = ?
    """, (email,)).fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User account not found.")

    if not user["is_active"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Account has been deactivated. Contact Head Master.")

    otp_record = conn.execute("""
        SELECT * FROM otp_codes
        WHERE LOWER(email) = ? AND purpose = ? AND is_used = 0
        ORDER BY id DESC LIMIT 1
    """, (email, purpose)).fetchone()

    if not otp_record:
        conn.close()
        raise HTTPException(status_code=400, detail="No active OTP found for this login method. Please request a new code.")

    expires_at = datetime.fromisoformat(otp_record["expires_at"].replace("Z", ""))
    if datetime.utcnow() > expires_at:
        conn.execute("UPDATE otp_codes SET is_used = 1 WHERE id = ?", (otp_record["id"],))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a fresh code.")

    if otp_record["attempts"] >= MAX_OTP_ATTEMPTS:
        conn.execute("UPDATE otp_codes SET is_used = 1 WHERE id = ?", (otp_record["id"],))
        conn.commit()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Too many incorrect attempts. This OTP has been invalidated for security."
        )

    if not verify_otp_hash(input_otp, email, otp_record["otp_hash"]):
        conn.execute("UPDATE otp_codes SET attempts = attempts + 1 WHERE id = ?", (otp_record["id"],))
        conn.commit()
        conn.close()
        remaining = MAX_OTP_ATTEMPTS - (otp_record["attempts"] + 1)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid OTP code. {remaining} attempt(s) remaining."
        )

    # Consume the OTP before issuing a token so it cannot be reused.
    conn.execute("UPDATE otp_codes SET is_used = 1 WHERE id = ?", (otp_record["id"],))

    token_data = {
        "user_id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "school_id": user["school_id"],
        "school_name": user["school_name"],
        "dise_code": user["dise_code"]
    }
    access_token = create_access_token(token_data)

    client_ip = request.client.host if request.client else "127.0.0.1"
    audit_action = "LOGIN_PASSWORD_OTP_SUCCESS" if purpose == "password_login" else "LOGIN_OTP_SUCCESS"
    record_audit(
        conn, user["school_id"], user["id"], user["full_name"], user["role"],
        audit_action, f"Successful {purpose} OTP login from {client_ip}", client_ip
    )
    conn.commit()
    conn.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data
    }


@app.post("/api/auth/login-password", summary="Login with Email, Password and OTP")
def login_password(payload: UserLoginPassword, request: Request):
    conn = get_db_connection()
    user = conn.execute("""
        SELECT u.*, s.name as school_name, s.dise_code
        FROM users u
        LEFT JOIN schools s ON u.school_id = s.id
        WHERE LOWER(u.email) = LOWER(?)
    """, (payload.email.strip(),)).fetchone()

    if not user or not verify_password(payload.password, user["password_hash"]):
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please try again."
        )

    if not user["is_active"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Account has been deactivated. Contact Head Master.")

    email = user["email"].strip().lower()
    try:
        response = create_and_send_auth_otp(conn, user, email, request, "password_login")
    except Exception:
        conn.rollback()
        conn.close()
        raise
    conn.close()
    return response


@app.post("/api/auth/firebase-login", summary="Authenticate via Firebase Auth (Google / OAuth)")
def firebase_login(payload: FirebaseAuthPayload, request: Request):
    conn = get_db_connection()
    email = (payload.email or "").strip().lower()
    full_name = (payload.full_name or "").strip() or "Google Official"
    role = (payload.role or "headmaster").strip().lower()

    if not email:
        conn.close()
        raise HTTPException(status_code=400, detail="Valid email is required from Firebase identity.")

    # Check if user already exists
    user = conn.execute("""
        SELECT u.*, s.name as school_name, s.dise_code
        FROM users u
        LEFT JOIN schools s ON u.school_id = s.id
        WHERE LOWER(u.email) = ?
    """, (email,)).fetchone()

    if not user:
        # Check if an institution exists to link this user to
        school = conn.execute("SELECT * FROM schools ORDER BY id ASC LIMIT 1").fetchone()
        cursor = conn.cursor()
        if not school:
            cursor.execute("""
                INSERT INTO schools (dise_code, name, name_kn, taluk, district, state)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("29210203001", "Karnataka PM POSHAN School", "ಕರ್ನಾಟಕ ಪಿಎಂ ಪೋಷಣ ಶಾಲೆ", "Belur", "Hassan", "Karnataka"))
            school_id = cursor.lastrowid
            school_name = "Karnataka PM POSHAN School"
            dise_code = "29210203001"
        else:
            school_id = school["id"]
            school_name = school["name"]
            dise_code = school["dise_code"]

        cursor.execute("""
            INSERT INTO users (school_id, full_name, email, phone, role, password_hash, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (school_id, full_name, email, "", role, "FIREBASE_OAUTH_AUTHED"))
        new_id = cursor.lastrowid
        conn.commit()

        user = {
            "id": new_id,
            "email": email,
            "full_name": full_name,
            "role": role,
            "school_id": school_id,
            "school_name": school_name,
            "dise_code": dise_code
        }
    else:
        user = dict(user)

    token_data = {
        "user_id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "school_id": user["school_id"],
        "school_name": user.get("school_name", "PM POSHAN School"),
        "dise_code": user.get("dise_code", "29210203001")
    }
    access_token = create_access_token(token_data)

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(conn, user["school_id"], user["id"], user["full_name"], user["role"],
                 "LOGIN_FIREBASE", f"Successful Firebase authentication for {email}", client_ip)
    conn.commit()
    conn.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data,
        "provider": "firebase"
    }

@app.post("/api/auth/meta-login", summary="Authenticate via Meta (Facebook) OAuth")
def meta_login(payload: MetaAuthPayload, request: Request):
    conn = get_db_connection()
    user_id = (payload.user_id or "").strip()
    full_name = (payload.full_name or "").strip() or "Meta Official"
    role = (payload.role or "headmaster").strip().lower()

    # Meta email or generate identity-linked identifier
    email = (payload.email or "").strip().lower()
    if not email:
        email = f"meta_{user_id}@school.karnataka.gov.in" if user_id else "meta.staff@school.karnataka.gov.in"

    user = conn.execute("""
        SELECT u.*, s.name as school_name, s.dise_code
        FROM users u
        LEFT JOIN schools s ON u.school_id = s.id
        WHERE LOWER(u.email) = ?
    """, (email,)).fetchone()

    if not user:
        school = conn.execute("SELECT * FROM schools ORDER BY id ASC LIMIT 1").fetchone()
        cursor = conn.cursor()
        if not school:
            cursor.execute("""
                INSERT INTO schools (dise_code, name, name_kn, taluk, district, state)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("29210203001", "Karnataka PM POSHAN School", "ಕರ್ನಾಟಕ ಪಿಎಂ ಪೋಷಣ ಶಾಲೆ", "Belur", "Hassan", "Karnataka"))
            school_id = cursor.lastrowid
            school_name = "Karnataka PM POSHAN School"
            dise_code = "29210203001"
        else:
            school_id = school["id"]
            school_name = school["name"]
            dise_code = school["dise_code"]

        cursor.execute("""
            INSERT INTO users (school_id, full_name, email, phone, role, password_hash, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (school_id, full_name, email, "", role, "META_OAUTH_AUTHED"))
        new_id = cursor.lastrowid
        conn.commit()

        user = {
            "id": new_id,
            "email": email,
            "full_name": full_name,
            "role": role,
            "school_id": school_id,
            "school_name": school_name,
            "dise_code": dise_code
        }
    else:
        user = dict(user)

    token_data = {
        "user_id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "school_id": user["school_id"],
        "school_name": user.get("school_name", "PM POSHAN School"),
        "dise_code": user.get("dise_code", "29210203001")
    }
    access_token = create_access_token(token_data)

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(conn, user["school_id"], user["id"], user["full_name"], user["role"],
                 "LOGIN_META", f"Successful Meta authentication for {email}", client_ip)
    conn.commit()
    conn.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data,
        "provider": "meta"
    }

@app.post("/api/auth/request-otp", summary="Generate & Send 6-Digit Passwordless Login OTP")
def request_otp(payload: UserRequestOTP, request: Request):
    email = payload.email.strip().lower()
    conn = get_db_connection()

    user = conn.execute("""
        SELECT u.*, s.name as school_name
        FROM users u
        LEFT JOIN schools s ON u.school_id = s.id
        WHERE LOWER(u.email) = ?
    """, (email,)).fetchone()

    if not user:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address. Please register or verify the email."
        )

    if not user["is_active"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Account has been deactivated. Contact Head Master.")

    try:
        response = create_and_send_auth_otp(conn, user, email, request, "passwordless_login")
    except Exception:
        conn.rollback()
        conn.close()
        raise

    conn.close()
    return response


@app.post("/api/auth/verify-otp", summary="Verify Passwordless Login OTP and Issue JWT")
def verify_otp(payload: UserVerifyOTP, request: Request):
    return complete_otp_login(payload, request, "passwordless_login")


@app.post("/api/auth/verify-password-otp", summary="Verify Password Login OTP and Issue JWT")
def verify_password_otp(payload: UserVerifyOTP, request: Request):
    return complete_otp_login(payload, request, "password_login")


@app.post("/api/auth/forgot-password", summary="Request Password Reset OTP via Email")
def forgot_password(payload: ForgotPasswordRequest, request: Request):
    email = payload.email.strip().lower()
    conn = get_db_connection()
    user = conn.execute("""
        SELECT u.*, s.name as school_name
        FROM users u
        LEFT JOIN schools s ON u.school_id = s.id
        WHERE LOWER(u.email) = ?
    """, (email,)).fetchone()

    if not user:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="No registered user account found with this email address."
        )

    if not user["is_active"]:
        conn.close()
        raise HTTPException(status_code=403, detail="This account has been deactivated.")

    # Rate limiting: wait 30 seconds between requests
    recent_otp = conn.execute("""
        SELECT id FROM otp_codes
        WHERE LOWER(email) = ? AND purpose = 'password_reset'
          AND created_at > datetime('now', '-30 seconds')
    """, (email,)).fetchone()

    if recent_otp:
        conn.close()
        raise HTTPException(
            status_code=429,
            detail="Please wait 30 seconds before requesting another password reset code."
        )

    # Invalidate previous unused reset OTPs
    conn.execute("""
        UPDATE otp_codes SET is_used = 1
        WHERE LOWER(email) = ? AND purpose = 'password_reset' AND is_used = 0
    """, (email,))

    otp_code = generate_secure_otp()
    hashed_otp = hash_otp(otp_code, email)
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    conn.execute("""
        INSERT INTO otp_codes (email, otp_hash, expires_at, purpose)
        VALUES (?, ?, ?, 'password_reset')
    """, (email, hashed_otp, expires_at))

    send_result = send_password_reset_email(email, otp_code, user["full_name"])

    if not send_result.get("success"):
        conn.rollback()
        conn.close()
        raise HTTPException(
            status_code=500,
            detail=send_result.get("error", "Failed to deliver password reset OTP email.")
        )

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(
        conn, user["school_id"], user["id"], user["full_name"], user["role"],
        "FORGOT_PASSWORD_REQUESTED", f"Password reset OTP generated for {email}", client_ip
    )
    conn.commit()
    conn.close()

    response = {
        "success": True,
        "message": f"Password reset verification code sent to {email}. Please check your email inbox.",
        "expires_in_minutes": OTP_EXPIRE_MINUTES,
        "email": email
    }
    if send_result.get("mode") in ["dev_simulator", "dev_fallback", "cloud_firewall_fallback"]:
        response["dev_preview_otp"] = otp_code

    return response


@app.post("/api/auth/reset-password", summary="Verify OTP and Set New Password")
def reset_password(payload: ResetPasswordRequest, request: Request):
    email = payload.email.strip().lower()
    input_otp = payload.otp_code.strip()
    new_password = payload.new_password.strip()

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")

    if len(input_otp) != 6 or not input_otp.isdigit():
        raise HTTPException(status_code=400, detail="Enter a valid 6-digit verification code.")

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User account not found.")

    otp_record = conn.execute("""
        SELECT * FROM otp_codes
        WHERE LOWER(email) = ? AND purpose = 'password_reset' AND is_used = 0
        ORDER BY id DESC LIMIT 1
    """, (email,)).fetchone()

    if not otp_record:
        conn.close()
        raise HTTPException(status_code=400, detail="No active password reset code found. Please request a new code.")

    expires_at = datetime.fromisoformat(otp_record["expires_at"].replace("Z", ""))
    if datetime.utcnow() > expires_at:
        conn.execute("UPDATE otp_codes SET is_used = 1 WHERE id = ?", (otp_record["id"],))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Password reset code has expired. Please request a fresh code.")

    if otp_record["attempts"] >= MAX_OTP_ATTEMPTS:
        conn.execute("UPDATE otp_codes SET is_used = 1 WHERE id = ?", (otp_record["id"],))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Too many incorrect attempts. This code has been invalidated.")

    if not verify_otp_hash(input_otp, email, otp_record["otp_hash"]):
        conn.execute("UPDATE otp_codes SET attempts = attempts + 1 WHERE id = ?", (otp_record["id"],))
        conn.commit()
        conn.close()
        remaining = MAX_OTP_ATTEMPTS - (otp_record["attempts"] + 1)
        raise HTTPException(status_code=400, detail=f"Invalid OTP code. {remaining} attempt(s) remaining.")

    # Mark OTP as used
    conn.execute("UPDATE otp_codes SET is_used = 1 WHERE id = ?", (otp_record["id"],))

    # Update password hash
    new_hash = hash_password(new_password)
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user["id"]))

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(
        conn, user["school_id"], user["id"], user["full_name"], user["role"],
        "PASSWORD_RESET_SUCCESS", f"Password successfully updated via OTP verification for {email}", client_ip
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Password reset successfully! You can now log in with your new password."
    }


@app.post("/api/auth/register", summary="Register New School Personnel with DISE Code")
def register_user(payload: UserRegister, request: Request):
    conn = get_db_connection()

    # Verify school by DISE code
    school = conn.execute("SELECT * FROM schools WHERE dise_code = ?", (payload.dise_code.strip(),)).fetchone()
    if not school:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"School with DISE Code '{payload.dise_code}' is not yet registered. Please configure the school first."
        )

    # Check email duplicate
    existing = conn.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (payload.email.strip(),)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    valid_roles = ["headmaster", "teacher", "kitchen_staff"]
    if payload.role not in valid_roles:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")

    pwd_hash = hash_password(payload.password)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (school_id, full_name, email, phone, role, password_hash)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (school["id"], payload.full_name.strip(), payload.email.strip().lower(), payload.phone, payload.role, pwd_hash))
    new_user_id = cursor.lastrowid

    token_data = {
        "user_id": new_user_id,
        "email": payload.email.strip().lower(),
        "full_name": payload.full_name.strip(),
        "role": payload.role,
        "school_id": school["id"],
        "school_name": school["name"],
        "dise_code": school["dise_code"]
    }
    access_token = create_access_token(token_data)

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(conn, school["id"], new_user_id, payload.full_name, payload.role,
                 "USER_REGISTRATION", f"New {payload.role} registered", client_ip)
    conn.commit()
    conn.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data
    }

@app.post("/api/school/setup", summary="Setup Initial School and Head Master / Admin Account")
def setup_school(payload: SchoolSetup, request: Request):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        existing_school = cursor.execute("SELECT id FROM schools WHERE dise_code = ?", (payload.dise_code.strip(),)).fetchone()
        if existing_school:
            raise HTTPException(status_code=400, detail="A school with this DISE code is already registered.")

        existing_user = cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (payload.email.strip(),)).fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="This email is already in use by another user account.")

        # 1. Insert School
        cursor.execute("""
            INSERT INTO schools (dise_code, name, name_kn, taluk, district, state, head_master_name, contact_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.dise_code.strip(),
            payload.name.strip(),
            payload.name_kn.strip() if payload.name_kn else payload.name.strip(),
            payload.taluk.strip(),
            payload.district.strip(),
            payload.state.strip(),
            payload.head_master_name.strip(),
            payload.phone
        ))
        school_id = cursor.lastrowid

        # 2. Insert Head Master User
        pwd_hash = hash_password(payload.password)
        cursor.execute("""
            INSERT INTO users (school_id, full_name, email, phone, role, password_hash)
            VALUES (?, ?, ?, ?, 'headmaster', ?)
        """, (
            school_id,
            payload.head_master_name.strip(),
            payload.email.strip().lower(),
            payload.phone,
            pwd_hash
        ))
        user_id = cursor.lastrowid

        # 3. Initialize Standard PM-POSHAN Inventory Categories (all stock starting at 0.0)
        standard_items = [
            ("RICE-RAW", "Rice", "ಅಕ್ಕಿ", "grains", "kg", "ಕೆ.ಜಿ", 0.0, 25.0, 100.0),
            ("WHEAT-FLR", "Wheat / Atta", "ಗೋಧಿ ಹಿಟ್ಟು", "grains", "kg", "ಕೆ.ಜಿ", 0.0, 15.0, 50.0),
            ("DAL-TOOR", "Toor Dal (Yellow Pigeon Pea)", "ತೊಗರಿ ಬೇಳೆ", "pulses", "kg", "ಕೆ.ಜಿ", 0.0, 15.0, 30.0),
            ("DAL-MOONG", "Moong Dal (Green Gram)", "ಹೆಸರು ಬೇಳೆ", "pulses", "kg", "ಕೆ.ಜಿ", 0.0, 10.0, 20.0),
            ("OIL-FORT", "Fortified Sunflower/Palm Oil", "ಅಡುಗೆ ಎಣ್ಣೆ", "oil", "liters", "ಲೀಟರ್", 0.0, 10.0, 5.0),
            ("EGG-POULTRY", "Eggs (Govt Certified)", "ಮೊಟ್ಟೆ", "dairy", "units", "ಸಂಖ್ಯೆ", 0.0, 50.0, 1.0),
            ("MILK-POWDER", "Ksheera Bhagya Milk Powder", "ಕ್ಷೀರ ಭಾಗ್ಯ ಹಾಲಿನ ಪುಡಿ", "dairy", "kg", "ಕೆ.ಜಿ", 0.0, 10.0, 15.0),
            ("SALT-IOD", "Iodized Salt", "ಅಯೋಡೈಸ್ಡ್ ಉಪ್ಪು", "spices", "kg", "ಕೆ.ಜಿ", 0.0, 5.0, 4.0),
            ("SPICE-SAMBAR", "Sambar Powder & Spices", "ಸಾಂಬಾರ್ ಮಸಾಲೆ ಪುಡಿ", "spices", "kg", "ಕೆ.ಜಿ", 0.0, 5.0, 3.0),
            ("CHIKKI-NUT", "Nutri Groundnut Chikki", "ಕಡಲೆಕಾಯಿ ಚಿಕ್ಕಿ", "produce", "units", "ಸಂಖ್ಯೆ", 0.0, 50.0, 1.0),
            ("BANANAS", "Fruit", "ಬಾಳೆಹಣ್ಣು", "Fruit", "units", "ಸಂಖ್ಯೆ", 0.0, 50.0, 1.0),
            ("LPG GAS", "Kitchen Essential", "", "LPS", "units", "ಸಂಖ್ಯೆ", 0.0, 50.0, 1.0)
        ]
        for code, iname, iname_kn, cat, unit, unit_kn, stock, min_th, norm in standard_items:
            cursor.execute("""
                INSERT OR IGNORE INTO inventory_items
                (school_id, item_code, name, name_kn, category, unit, unit_kn, current_stock, min_threshold, norm_per_student_grams)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (school_id, code, iname, iname_kn, cat, unit, unit_kn, stock, min_th, norm))

        # 4. Standard Classes with 0 students enrolled
        standard_classes = [
            ("Class 8", "೮ನೇ ತರಗತಿ", "A"),
            ("Class 9", "೯ನೇ ತರಗತಿ", "A"),
            ("Class 10", "೧೦ನೇ ತರಗತಿ", "A")
        ]
        for cname, cname_kn, sec in standard_classes:
            cursor.execute("""
                INSERT INTO classes (school_id, grade_name, grade_name_kn, section, total_enrolled, boys_enrolled, girls_enrolled)
                VALUES (?, ?, ?, ?, 0, 0, 0)
            """, (school_id, cname, cname_kn, sec))

        client_ip = request.client.host if request.client else "127.0.0.1"
        record_audit(conn, school_id, user_id, payload.head_master_name, "headmaster",
                     "SCHOOL_SETUP", f"Institution '{payload.name}' registered with DISE {payload.dise_code}", client_ip)
        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to setup school: {str(e)}")
    finally:
        conn.close()

    token_data = {
        "user_id": user_id,
        "email": payload.email.strip().lower(),
        "full_name": payload.head_master_name.strip(),
        "role": "headmaster",
        "school_id": school_id,
        "school_name": payload.name.strip(),
        "dise_code": payload.dise_code.strip()
    }
    access_token = create_access_token(token_data)
    return {
        "message": "School successfully configured",
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data
    }

@app.get("/api/auth/me", summary="Get Current Authenticated User Profile")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

# ==========================================
# 2. DASHBOARD & SUMMARY ENDPOINT
# ==========================================

@app.get("/api/dashboard/summary", summary="Comprehensive Daily Dashboard Statistics")
def get_dashboard_summary(target_date: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    school_id = current_user["school_id"]
    query_date = target_date or date.today().isoformat()

    conn = get_db_connection()

    # School details
    school = conn.execute("SELECT * FROM schools WHERE id = ?", (school_id,)).fetchone()

    # Total enrolled students
    enrollment = conn.execute("""
        SELECT SUM(total_enrolled) as total, SUM(boys_enrolled) as boys, SUM(girls_enrolled) as girls
        FROM classes WHERE school_id = ?
    """, (school_id,)).fetchone()

    total_enrolled = enrollment["total"] or 0

    # Today's marked attendance
    att_summary = conn.execute("""
        SELECT SUM(total_present) as total_present, SUM(boys_present) as boys_present, SUM(girls_present) as girls_present,
               COUNT(id) as classes_marked
        FROM attendance_records
        WHERE school_id = ? AND date = ?
    """, (school_id, query_date)).fetchone()

    total_classes = conn.execute("SELECT COUNT(*) FROM classes WHERE school_id = ?", (school_id,)).fetchone()[0]

    # Today's meal log
    meal_log = conn.execute("""
        SELECT * FROM meal_records WHERE school_id = ? AND date = ?
    """, (school_id, query_date)).fetchone()

    # Critical inventory items & low stock alerts
    inventory_rows = conn.execute("""
        SELECT id, item_code, name, name_kn, category, unit, unit_kn, current_stock, min_threshold, norm_per_student_grams
        FROM inventory_items
        WHERE school_id = ?
        ORDER BY category ASC, name ASC
    """, (school_id,)).fetchall()

    items = []
    low_stock_alerts = []
    daily_consumption_estimate = {}

    for row in inventory_rows:
        item_dict = dict(row)
        # Calculate days of stock remaining based on enrolled students
        daily_req = (item_dict["norm_per_student_grams"] * total_enrolled) / (1000.0 if item_dict["unit"] == "kg" else 1.0)
        item_dict["daily_requirement_est"] = round(daily_req, 2)
        days_remaining = round(item_dict["current_stock"] / daily_req, 1) if daily_req > 0 else 999.0
        item_dict["days_remaining"] = days_remaining
        item_dict["is_low_stock"] = item_dict["current_stock"] <= item_dict["min_threshold"]

        if item_dict["is_low_stock"]:
            low_stock_alerts.append({
                "item_code": item_dict["item_code"],
                "name": item_dict["name"],
                "name_kn": item_dict["name_kn"],
                "current_stock": item_dict["current_stock"],
                "unit": item_dict["unit"],
                "unit_kn": item_dict["unit_kn"],
                "days_remaining": days_remaining
            })
        items.append(item_dict)

    conn.close()

    return {
        "date": query_date,
        "school": {
            "name": school["name"],
            "name_kn": school["name_kn"],
            "dise_code": school["dise_code"],
            "taluk": school["taluk"],
            "district": school["district"],
            "head_master": school["head_master_name"]
        },
        "enrollment": {
            "total": total_enrolled,
            "boys": enrollment["boys"] or 0,
            "girls": enrollment["girls"] or 0
        },
        "attendance": {
            "total_present": att_summary["total_present"] or 0,
            "boys_present": att_summary["boys_present"] or 0,
            "girls_present": att_summary["girls_present"] or 0,
            "percentage": round(((att_summary["total_present"] or 0) / total_enrolled * 100), 1) if total_enrolled else 0,
            "classes_marked": att_summary["classes_marked"] or 0,
            "total_classes": total_classes,
            "is_complete": (att_summary["classes_marked"] or 0) >= total_classes
        },
        "meal": {
            "is_logged": bool(meal_log),
            "beneficiaries_served": meal_log["beneficiaries_served"] if meal_log else 0,
            "ksheera_bhagya_milk": meal_log["ksheera_bhagya_milk_count"] if meal_log else 0,
            "eggs_distributed": meal_log["eggs_distributed"] if meal_log else 0,
            "bananas_distributed": meal_log["bananas_distributed"] if meal_log else 0,
            "chikki_distributed": meal_log["chikki_distributed"] if meal_log else 0,
            "menu_type": meal_log["menu_type"] if meal_log else "Not logged yet",
            "menu_type_kn": meal_log["menu_type_kn"] if meal_log else "ಇನ್ನೂ ದಾಖಲಾಗಿಲ್ಲ",
            "tasting_score": meal_log["tasting_score"] if meal_log else 5,
            "tasting_notes": meal_log["tasting_notes"] if meal_log else None,
            "tasted_by": meal_log["tasted_by"] if meal_log else None
        },
        "inventory": {
            "items": items,
            "low_stock_alerts": low_stock_alerts
        }
    }

# ==========================================
# 3. STUDENT ATTENDANCE MODULE
# ==========================================

def ensure_school_classes(conn, school_id: int):
    """Ensure standard Karnataka school classes (Class 1-10) exist for a school."""
    count = conn.execute("SELECT COUNT(*) FROM classes WHERE school_id = ?", (school_id,)).fetchone()[0]
    if count == 0:
        standard_classes = [
            
            ("Class 8", "೮ನೇ ತರಗತಿ", "A"),
            ("Class 9", "೯ನೇ ತರಗತಿ", "A"),
            ("Class 10", "೧೦ನೇ ತರಗತಿ", "A")
        ]
        for cname, cname_kn, sec in standard_classes:
            conn.execute("""
                INSERT INTO classes (school_id, grade_name, grade_name_kn, section, total_enrolled, boys_enrolled, girls_enrolled)
                VALUES (?, ?, ?, ?, 0, 0, 0)
            """, (school_id, cname, cname_kn, sec))
        conn.commit()

@app.get("/api/classes", summary="List School Classes and Student Counts")
@app.get("/api/attendance/classes", summary="List School Classes and Student Counts (Attendance Route)")
def list_classes(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    ensure_school_classes(conn, current_user["school_id"])
    classes = conn.execute("""
        SELECT * FROM classes WHERE school_id = ? ORDER BY id ASC
    """, (current_user["school_id"],)).fetchall()
    conn.close()
    return {"classes": [dict(c) for c in classes]}

@app.get("/api/attendance/records", summary="Get Attendance for a specific date")
def get_attendance(date_str: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    school_id = current_user["school_id"]
    query_date = date_str or date.today().isoformat()

    conn = get_db_connection()
    records = conn.execute("""
        SELECT c.id as class_id, c.grade_name, c.grade_name_kn, c.section,
               c.total_enrolled, c.boys_enrolled, c.girls_enrolled,
               ar.id as record_id, ar.total_present, ar.boys_present, ar.girls_present,
               ar.status, ar.remarks
        FROM classes c
        LEFT JOIN attendance_records ar ON c.id = ar.class_id AND ar.date = ?
        WHERE c.school_id = ?
        ORDER BY c.id ASC
    """, (query_date, school_id)).fetchall()

    conn.close()
    return {
        "date": query_date,
        "records": [dict(r) for r in records]
    }

@app.get("/api/school/info", summary="General School Information")
def get_school_info():
    conn = get_db_connection()
    school = conn.execute("SELECT * FROM schools LIMIT 1").fetchone()
    conn.close()
    if not school:
        return {
            "registered": False,
            "id": 0,
            "dise_code": "",
            "name": "PM POSHAN School Portal",
            "name_kn": "ಪಿಎಂ ಪೋಷಣ್ ಶಾಲಾ ಪೋರ್ಟಲ್",
            "taluk": "",
            "district": "",
            "state": "Karnataka",
            "head_master_name": ""
        }
    data = dict(school)
    data["registered"] = True
    return data

@app.get("/api/attendance/classes", summary="List Classes (Alias)")
def get_attendance_classes():
    conn = get_db_connection()
    classes = conn.execute("SELECT * FROM classes ORDER BY id ASC").fetchall()
    conn.close()
    return {"classes": [dict(c) for c in classes]}

@app.get("/api/classes/{class_id}/students", summary="Get Students Enrolled in a Specific Class")
def get_class_students(class_id: int):
    conn = get_db_connection()
    students = conn.execute("""
        SELECT * FROM students WHERE class_id = ? AND is_active = 1 ORDER BY roll_no ASC, name ASC
    """, (class_id,)).fetchall()
    conn.close()
    return {"class_id": class_id, "students": [dict(s) for s in students]}

@app.post("/api/classes/{class_id}/students", summary="Add Student to Class")
async def add_student_to_class(class_id: int, request: Request, current_user: dict = Depends(require_roles(["headmaster", "teacher"]))):
    body = await request.json()
    roll_no = body.get("roll_no")
    name = (body.get("name") or "").strip()
    name_kn = (body.get("name_kn") or "").strip()
    gender = body.get("gender", "M")
    diet = body.get("diet_preference", "egg")

    if not name:
        raise HTTPException(status_code=400, detail="Student name is required")

    conn = get_db_connection()
    cursor = conn.cursor()
    if not roll_no:
        max_roll = cursor.execute("SELECT MAX(roll_no) FROM students WHERE class_id = ?", (class_id,)).fetchone()[0]
        roll_no = (max_roll or 0) + 1

    cursor.execute("""
        INSERT INTO students (class_id, roll_no, name, name_kn, gender, diet_preference)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (class_id, roll_no, name, name_kn, gender, diet))

    # Update enrolled counts
    totals = cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) as boys,
               SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) as girls
        FROM students WHERE class_id = ? AND is_active = 1
    """, (class_id,)).fetchone()

    cursor.execute("""
        UPDATE classes
        SET total_enrolled = ?, boys_enrolled = ?, girls_enrolled = ?
        WHERE id = ?
    """, (totals["total"] or 0, totals["boys"] or 0, totals["girls"] or 0, class_id))

    conn.commit()
    conn.close()
    return {"success": True, "roll_no": roll_no, "name": name}

@app.post("/api/attendance/submit", summary="Submit Daily Class Attendance (Teacher/HM)")
def submit_attendance(payload: AttendanceSubmission, request: Request,
                      current_user: dict = Depends(require_roles(["headmaster", "teacher"]))):
    school_id = current_user["school_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    items_to_process = payload.items or []
    if not items_to_process and payload.class_id:
        items_to_process = [AttendanceItem(
            class_id=payload.class_id,
            total_present=payload.total_present or ((payload.boys_present or 0) + (payload.girls_present or 0)),
            boys_present=payload.boys_present or 0,
            girls_present=payload.girls_present or 0,
            remarks=payload.remarks
        )]

    total_submitted = 0
    for item in items_to_process:
        # Check that present count does not exceed enrollment
        cls = conn.execute("SELECT total_enrolled, boys_enrolled, girls_enrolled FROM classes WHERE id = ?", (item.class_id,)).fetchone()
        if not cls:
            continue

        if item.boys_present > cls["boys_enrolled"] or item.girls_present > cls["girls_enrolled"]:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Present count cannot exceed enrolled students for Class ID {item.class_id}."
            )

        total_present = item.boys_present + item.girls_present

        cursor.execute("""
            INSERT INTO attendance_records (school_id, class_id, date, total_present, boys_present, girls_present, marked_by, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(class_id, date) DO UPDATE SET
                total_present = excluded.total_present,
                boys_present = excluded.boys_present,
                girls_present = excluded.girls_present,
                marked_by = excluded.marked_by,
                remarks = excluded.remarks
        """, (school_id, item.class_id, payload.date, total_present, item.boys_present, item.girls_present, current_user["user_id"], item.remarks))
        total_submitted += total_present

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(conn, school_id, current_user.get("user_id"), current_user.get("full_name") or current_user.get("email", "Staff"), current_user.get("role", "staff"),
                 "ATTENDANCE_LOGGED", f"Logged attendance for date {payload.date} (Total: {total_submitted})", client_ip)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "date": payload.date,
        "total_marked": total_submitted,
        "message": "ಹಾಜರಾತಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ನಮೂದಿಸಲಾಗಿದೆ / Attendance successfully recorded."
    }

# ==========================================
# 4. MID-DAY MEAL TRACKING & STOCK DEDUCTION
# ==========================================

def save_geotag_photo_bytes(photo_data: str, school_id: int, date_str: str) -> Optional[str]:
    """Decodes a base64 geotagged plate photo and saves to frontend/uploads/meals/"""
    if not photo_data:
        return None
    try:
        if photo_data.startswith("/static/"):
            return photo_data
        
        header, b64_str = photo_data.split(",", 1) if "," in photo_data else ("", photo_data)
        image_bytes = base64.b64decode(b64_str)
        
        filename = f"plate_{school_id}_{date_str}_{int(datetime.now().timestamp())}.jpg"
        save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "uploads", "meals")
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(image_bytes)
            
        return f"/static/uploads/meals/{filename}"
    except Exception as e:
        print(f"[Photo Save Error] {e}")
        return None

@app.post("/api/meals/upload-geotag-photo", summary="Upload and Verify Geotagged Mid-Day Meal Plate Photo")
def upload_geotag_photo(payload: GeotagPhotoUpload, request: Request,
                        current_user: dict = Depends(require_roles(["headmaster", "teacher", "kitchen_staff"]))):
    school_id = current_user["school_id"]
    today_str = date.today().isoformat()
    photo_url = save_geotag_photo_bytes(payload.photo_data, school_id, today_str)
    if not photo_url:
        raise HTTPException(status_code=400, detail="Invalid photo image data provided.")
    
    acc = payload.accuracy_meters
    acc_status = "HIGH_ACCURACY" if (acc is not None and acc <= 15) else "MEDIUM_ACCURACY" if (acc is not None and acc <= 50) else "CALIBRATED"
    
    conn = get_db_connection()
    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(conn, school_id, current_user.get("user_id"), current_user.get("full_name") or current_user.get("email", "Staff"), current_user.get("role", "staff"),
                 "GEOTAG_PHOTO_CAPTURED",
                 f"Plate photo captured with GPS Lat={payload.latitude}, Lng={payload.longitude}, Acc=±{acc}m ({acc_status})", client_ip)
    conn.commit()
    conn.close()
                 
    return {
        "success": True,
        "photo_url": photo_url,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "accuracy_meters": payload.accuracy_meters,
        "timestamp": payload.timestamp or datetime.now().strftime("%d-%b-%Y %I:%M:%S %p"),
        "accuracy_status": acc_status
    }

@app.post("/api/meals/submit", summary="Log Daily Meals Served & Auto-Calculate Stock Consumption")
def submit_meal_record(payload: MealRecordCreate, request: Request,
                       current_user: dict = Depends(require_roles(["headmaster", "teacher", "kitchen_staff"]))):
    school_id = current_user["school_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Validation: Beneficiaries cannot exceed total present attendance
    att_row = conn.execute("""
        SELECT SUM(total_present) as total_present
        FROM attendance_records
        WHERE school_id = ? AND date = ?
    """, (school_id, payload.date)).fetchone()

    total_present = att_row["total_present"] if (att_row and att_row["total_present"]) else None
    if total_present is not None and payload.beneficiaries_served > total_present:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"Beneficiaries count ({payload.beneficiaries_served}) cannot exceed total marked attendance ({total_present}) for {payload.date}."
        )

    # Process and save geotagged photo if provided
    photo_url = save_geotag_photo_bytes(payload.photo_data, school_id, payload.date) if payload.photo_data else None

    # Upsert meal record with GPS Geotag metadata
    cursor.execute("""
        INSERT INTO meal_records (
            school_id, date, beneficiaries_served, ksheera_bhagya_milk_count,
            eggs_distributed, bananas_distributed, chikki_distributed,
            menu_type, menu_type_kn, tasting_score, tasting_notes, tasted_by, logged_by,
            photo_url, photo_lat, photo_lng, photo_accuracy, photo_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            beneficiaries_served = excluded.beneficiaries_served,
            ksheera_bhagya_milk_count = excluded.ksheera_bhagya_milk_count,
            eggs_distributed = excluded.eggs_distributed,
            bananas_distributed = excluded.bananas_distributed,
            chikki_distributed = excluded.chikki_distributed,
            menu_type = excluded.menu_type,
            menu_type_kn = excluded.menu_type_kn,
            tasting_score = excluded.tasting_score,
            tasting_notes = excluded.tasting_notes,
            tasted_by = excluded.tasted_by,
            logged_by = excluded.logged_by,
            photo_url = COALESCE(excluded.photo_url, meal_records.photo_url),
            photo_lat = COALESCE(excluded.photo_lat, meal_records.photo_lat),
            photo_lng = COALESCE(excluded.photo_lng, meal_records.photo_lng),
            photo_accuracy = COALESCE(excluded.photo_accuracy, meal_records.photo_accuracy),
            photo_timestamp = COALESCE(excluded.photo_timestamp, meal_records.photo_timestamp)
    """, (
        school_id, payload.date, payload.beneficiaries_served, payload.ksheera_bhagya_milk_count,
        payload.eggs_distributed, payload.bananas_distributed, payload.chikki_distributed,
        payload.menu_type, payload.menu_type_kn, payload.tasting_score, payload.tasting_notes,
        payload.tasted_by, current_user["user_id"],
        photo_url, payload.photo_lat, payload.photo_lng, payload.photo_accuracy, payload.photo_timestamp
    ))

    # AUTOMATED INVENTORY CONSUMPTION CALCULATION
    # Deduct standard PM POSHAN per-child weight norms
    beneficiaries = payload.beneficiaries_served
    consumption_map = {
        "RICE": round((beneficiaries * 150.0) / 1000.0, 2),        # 150g per student = kg
        "TUR_DAL": round((beneficiaries * 30.0) / 1000.0, 2),       # 30g per student = kg
        "OIL": round((beneficiaries * 7.5) / 1000.0, 2),           # 7.5g per student = L
        "SALT": round((beneficiaries * 4.0) / 1000.0, 2),          # 4g per student = kg
        "VEG_MIX": round((beneficiaries * 75.0) / 1000.0, 2),      # 75g fresh veg = kg
        "MILK_POWDER": round((payload.ksheera_bhagya_milk_count * 15.0) / 1000.0, 2), # 15g per milk serving
        "EGGS": float(payload.eggs_distributed),
        "BANANAS": float(payload.bananas_distributed),
        "CHIKKI": float(payload.chikki_distributed)
    }

    deductions_applied = []
    for item_code, quantity in consumption_map.items():
        if quantity <= 0:
            continue

        item = conn.execute("SELECT id, current_stock, unit FROM inventory_items WHERE school_id = ? AND item_code = ?",
                            (school_id, item_code)).fetchone()
        if item:
            new_stock = max(0.0, round(item["current_stock"] - quantity, 2))
            # Update item balance
            cursor.execute("UPDATE inventory_items SET current_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                           (new_stock, item["id"]))
            # Log OUTWARD stock transaction
            cursor.execute("""
                INSERT INTO stock_transactions (
                    school_id, item_id, transaction_type, quantity, balance_after,
                    notes, date, recorded_by
                ) VALUES (?, ?, 'OUTWARD', ?, ?, ?, ?, ?)
            """, (
                school_id, item["id"], quantity, new_stock,
                f"Auto-deducted for {beneficiaries} meal servings on {payload.date}",
                payload.date, current_user["user_id"]
            ))
            deductions_applied.append({
                "item_code": item_code,
                "consumed": quantity,
                "balance": new_stock
            })

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(conn, school_id, current_user.get("user_id"), current_user.get("full_name") or current_user.get("email", "Staff"), current_user.get("role", "staff"),
                 "MEAL_RECORD_SAVED",
                 f"Logged {beneficiaries} meals on {payload.date}. Auto-deducted inventory.", client_ip)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "date": payload.date,
        "beneficiaries": payload.beneficiaries_served,
        "deductions": deductions_applied,
        "message": "ಮಧ್ಯಾಹ್ನದ ಊಟದ ವಿವರ ಮತ್ತು ದಾಸ್ತಾನು ಕಡಿತ ಯಶಸ್ವಿಯಾಗಿ ದಾಖಲಾಗಿದೆ / Meal log and automated stock deduction saved."
    }

@app.post("/api/meal/record", summary="Log Daily Meal Record (Alias)")
def record_meal_alias(payload: MealRecordCreate, request: Request,
                      current_user: dict = Depends(require_roles(["headmaster", "teacher", "kitchen_staff"]))):
    return submit_meal_record(payload, request, current_user)

@app.get("/api/meal/today", summary="Fetch Today's Meal Record (Public/Staff)")
def get_today_meal(school_id: Optional[int] = None):
    conn = get_db_connection()
    today_str = date.today().isoformat()
    if school_id:
        meal = conn.execute("SELECT * FROM meal_records WHERE school_id = ? AND date = ? ORDER BY id DESC LIMIT 1", (school_id, today_str)).fetchone()
    else:
        meal = conn.execute("SELECT * FROM meal_records WHERE date = ? ORDER BY id DESC LIMIT 1", (today_str,)).fetchone()
    conn.close()
    return {"date": today_str, "meal_record": dict(meal) if meal else None}

@app.get("/api/meals/history", summary="Fetch Historical Meal Records")
def get_meal_history(limit: int = 30, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    meals = conn.execute("""
        SELECT mr.*, u.full_name as logged_by_name
        FROM meal_records mr
        LEFT JOIN users u ON mr.logged_by = u.id
        WHERE mr.school_id = ?
        ORDER BY mr.date DESC
        LIMIT ?
    """, (current_user["school_id"], limit)).fetchall()
    conn.close()
    return {"history": [dict(m) for m in meals]}

# ==========================================
# 5. INVENTORY & FRESH PRODUCE ENDPOINTS
# ==========================================

@app.get("/api/inventory/items", summary="List All Inventory Stocks and Status")
def get_inventory_items(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    items = conn.execute("""
        SELECT * FROM inventory_items WHERE school_id = ? ORDER BY category, name
    """, (current_user["school_id"],)).fetchall()
    conn.close()
    return {"items": [dict(i) for i in items]}

@app.post("/api/inventory/inward", summary="Record Stock Receipt (Ration Delivery / Purchase)")
def add_stock_inward(payload: StockInwardCreate, request: Request,
                     current_user: dict = Depends(require_roles(["headmaster", "kitchen_staff", "teacher"]))):
    school_id = current_user["school_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    item = conn.execute("SELECT * FROM inventory_items WHERE id = ? AND school_id = ?",
                        (payload.item_id, school_id)).fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Inventory item not found.")

    new_stock = round(item["current_stock"] + payload.quantity, 2)
    cursor.execute("UPDATE inventory_items SET current_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                   (new_stock, item["id"]))

    cursor.execute("""
        INSERT INTO stock_transactions (
            school_id, item_id, transaction_type, quantity, balance_after,
            vendor_name, bill_number, cost, notes, date, recorded_by
        ) VALUES (?, ?, 'INWARD', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        school_id, item["id"], payload.quantity, new_stock,
        payload.vendor_name, payload.bill_number, payload.cost,
        payload.notes, payload.date, current_user["user_id"]
    ))

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(conn, school_id, current_user.get("user_id"), current_user.get("full_name") or current_user.get("email", "Staff"), current_user.get("role", "staff"),
                 "STOCK_INWARD",
                 f"Added +{payload.quantity} {item['unit']} of {item['name']}. Bill: {payload.bill_number}", client_ip)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "item_name": item["name"],
        "added_quantity": payload.quantity,
        "new_stock": new_stock,
        "message": "ದಾಸ್ತಾನು ಸ್ವೀಕೃತಿ ಯಶಸ್ವಿಯಾಗಿ ಸೇರಿಸಲಾಗಿದೆ / Stock receipt recorded successfully."
    }

@app.post("/api/inventory/fresh-produce", summary="Log Perishable Fresh Produce (Vegetables/Greens/Fruits)")
def add_fresh_produce(payload: FreshProduceCreate, request: Request,
                      current_user: dict = Depends(require_roles(["headmaster", "kitchen_staff", "teacher"]))):
    school_id = current_user["school_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find or create produce item
    code = f"PRODUCE_{payload.item_name.upper().replace(' ', '_')}"
    existing = conn.execute("SELECT id, current_stock FROM inventory_items WHERE school_id = ? AND item_code = ?",
                            (school_id, code)).fetchone()

    if existing:
        new_stock = round(existing["current_stock"] + payload.quantity_kg, 2)
        cursor.execute("UPDATE inventory_items SET current_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                       (new_stock, existing["id"]))
        item_id = existing["id"]
    else:
        cursor.execute("""
            INSERT INTO inventory_items (school_id, item_code, name, name_kn, category, unit, unit_kn, current_stock, min_threshold, norm_per_student_grams)
            VALUES (?, ?, ?, ?, 'produce', 'kg', 'ಕೆ.ಜಿ', ?, 5.0, 75.0)
        """, (school_id, code, payload.item_name, payload.item_name_kn, payload.quantity_kg))
        item_id = cursor.lastrowid
        new_stock = payload.quantity_kg

    cursor.execute("""
        INSERT INTO stock_transactions (
            school_id, item_id, transaction_type, quantity, balance_after,
            vendor_name, bill_number, cost, notes, date, recorded_by
        ) VALUES (?, ?, 'INWARD', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        school_id, item_id, payload.quantity_kg, new_stock,
        payload.vendor_name, payload.bill_no, payload.cost,
        payload.notes or "Fresh vegetables/produce purchase", payload.date, current_user["user_id"]
    ))

    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit(conn, school_id, current_user.get("user_id"), current_user.get("full_name") or current_user.get("email", "Staff"), current_user.get("role", "staff"),
                 "FRESH_PRODUCE_LOG",
                 f"Fresh produce received: {payload.quantity_kg} kg of {payload.item_name}", client_ip)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "produce": payload.item_name,
        "quantity_kg": payload.quantity_kg,
        "new_stock": new_stock,
        "message": "ತಾಜಾ ತರಕಾರಿಗಳ ಖರೀದಿ ಯಶಸ್ವಿಯಾಗಿ ದಾಖಲಾಗಿದೆ / Fresh produce recorded."
    }

@app.get("/api/inventory/transactions", summary="Stock Ledger Transactions History")
def get_stock_transactions(limit: int = 50, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    txs = conn.execute("""
        SELECT st.*, ii.name as item_name, ii.name_kn as item_name_kn, ii.unit, u.full_name as recorded_by_name
        FROM stock_transactions st
        JOIN inventory_items ii ON st.item_id = ii.id
        LEFT JOIN users u ON st.recorded_by = u.id
        WHERE st.school_id = ?
        ORDER BY st.id DESC
        LIMIT ?
    """, (current_user["school_id"], limit)).fetchall()
    conn.close()
    return {"transactions": [dict(t) for t in txs]}

# ==========================================
# 6. MONTHLY COMPLIANCE & AUDIT REPORTS
# ==========================================

@app.get("/api/reports/monthly", summary="Official Karnataka PM-POSHAN Monthly Review Report")
def get_monthly_report(year_month: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """
    Format compliant with Karnataka Akshara Dasoha monthly report submitted to BEO.
    year_month format: 'YYYY-MM' (e.g. '2026-09')
    """
    school_id = current_user["school_id"]
    target_ym = year_month or datetime.now().strftime("%Y-%m")

    conn = get_db_connection()
    school = conn.execute("SELECT * FROM schools WHERE id = ?", (school_id,)).fetchone()

    # Working days & total meals served in month
    meal_stats = conn.execute("""
        SELECT COUNT(id) as working_days,
               SUM(beneficiaries_served) as total_meals_served,
               SUM(ksheera_bhagya_milk_count) as total_milk_served,
               SUM(eggs_distributed) as total_eggs,
               SUM(bananas_distributed) as total_bananas,
               SUM(chikki_distributed) as total_chikki,
               AVG(beneficiaries_served) as avg_daily_meals
        FROM meal_records
        WHERE school_id = ? AND strftime('%Y-%m', date) = ?
    """, (school_id, target_ym)).fetchone()

    # Monthly consumption per item
    stock_consumed = conn.execute("""
        SELECT ii.item_code, ii.name, ii.name_kn, ii.unit,
               SUM(st.quantity) as total_consumed
        FROM stock_transactions st
        JOIN inventory_items ii ON st.item_id = ii.id
        WHERE st.school_id = ? AND st.transaction_type = 'OUTWARD' AND strftime('%Y-%m', st.date) = ?
        GROUP BY ii.id
    """, (school_id, target_ym)).fetchall()

    # Monthly stock received (Inward)
    stock_received = conn.execute("""
        SELECT ii.item_code, ii.name, ii.name_kn, ii.unit,
               SUM(st.quantity) as total_received,
               SUM(st.cost) as total_cost
        FROM stock_transactions st
        JOIN inventory_items ii ON st.item_id = ii.id
        WHERE st.school_id = ? AND st.transaction_type = 'INWARD' AND strftime('%Y-%m', st.date) = ?
        GROUP BY ii.id
    """, (school_id, target_ym)).fetchall()

    conn.close()

    return {
        "month": target_ym,
        "school": {
            "name": school["name"],
            "name_kn": school["name_kn"],
            "dise_code": school["dise_code"],
            "taluk": school["taluk"],
            "district": school["district"],
            "head_master": school["head_master_name"]
        },
        "working_days": meal_stats["working_days"] or 0,
        "total_meals_served": meal_stats["total_meals_served"] or 0,
        "avg_daily_meals": round(meal_stats["avg_daily_meals"] or 0, 1),
        "total_milk_served": meal_stats["total_milk_served"] or 0,
        "total_eggs": meal_stats["total_eggs"] or 0,
        "total_bananas": meal_stats["total_bananas"] or 0,
        "total_chikki": meal_stats["total_chikki"] or 0,
        "consumption_breakdown": [dict(c) for c in stock_consumed],
        "receipt_breakdown": [dict(r) for r in stock_received]
    }

@app.get("/api/audit/logs", summary="Tamper-evident Security Audit Trail")
def get_audit_trail(limit: int = 50, current_user: dict = Depends(require_roles(["headmaster", "admin"]))):
    conn = get_db_connection()
    logs = conn.execute("""
        SELECT * FROM audit_logs
        WHERE school_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (current_user["school_id"], limit)).fetchall()
    conn.close()
    return {"logs": [dict(l) for l in logs]}

# ==========================================
# 7. INTEGRATION & CLOUD CONFIG ENDPOINTS
# ==========================================

@app.get("/api/config/public", summary="Public Integration Config (Firebase, Meta, Stitch)")
def get_public_config():
    return {
        "firebase": get_public_firebase_config(),
        "meta": get_meta_config(),
        "stitch": get_stitch_config(),
        "latest_dev_otps": list(LATEST_DEV_OTPS.values())[-5:] if LATEST_DEV_OTPS else []
    }

@app.post("/api/config/update-keys", summary="Update API Keys (Firebase, Stitch, Meta)")
def update_keys(payload: RuntimeKeysPayload):
    res = update_runtime_keys(payload.firebase, payload.meta, payload.stitch)
    return {
        "success": True,
        "status": res,
        "message": "API keys updated successfully."
    }

@app.get("/api/network-info", summary="LAN IP and Dual-Device Access Information")
def get_network_info():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        lan_ip = s.getsockname()[0]
    except Exception:
        try:
            s.connect(('8.8.8.8', 80))
            lan_ip = s.getsockname()[0]
        except Exception:
            lan_ip = '127.0.0.1'
    finally:
        s.close()
    
    port = int(os.getenv("PORT", "8000"))
    return {
        "lan_ip": lan_ip,
        "port": port,
        "mobile_url": f"http://{lan_ip}:{port}/",
        "desktop_url": f"http://localhost:{port}/"
    }

# ==========================================
# 8. STATIC FILES & SINGLE PAGE APP SERVING
# ==========================================

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index():
        resp = FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    @app.get("/manifest.json", include_in_schema=False)
    def serve_manifest():
        resp = FileResponse(os.path.join(FRONTEND_DIR, "manifest.json"), media_type="application/manifest+json")
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return resp

    @app.get("/sw.js", include_in_schema=False)
    def serve_sw():
        resp = FileResponse(os.path.join(FRONTEND_DIR, "sw.js"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return resp

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
