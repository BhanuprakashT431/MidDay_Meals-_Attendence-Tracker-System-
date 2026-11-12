"""
Database module for PM-POSHAN Mid-Day Meal and Attendance Management System
Configurable for any Karnataka Government / Aided Educational Institution.
"""

import sqlite3
import os
import json
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "midday_meal.db")

def get_db_connection():
    """Create and return a database connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 20000")
    except Exception:
        pass
    return conn

def init_db():
    """Initialize database tables and seed initial data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Schools table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dise_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        name_kn TEXT NOT NULL,
        taluk TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT DEFAULT 'Karnataka',
        head_master_name TEXT,
        contact_phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER REFERENCES schools(id),
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        role TEXT NOT NULL CHECK(role IN ('headmaster', 'teacher', 'kitchen_staff', 'admin')),
        password_hash TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # OTP codes table for secure OTP-based login
    # The purpose column keeps password and passwordless login OTPs separate.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        otp_hash TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        attempts INTEGER DEFAULT 0,
        is_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        purpose TEXT NOT NULL DEFAULT 'passwordless_login'
    );
    """)

    # Add the purpose column to existing databases without deleting any OTP records.
    # Existing OTP records remain valid for the passwordless login flow.
    cursor.execute("PRAGMA table_info(otp_codes)")
    otp_columns = {row["name"] for row in cursor.fetchall()}
    if "purpose" not in otp_columns:
        cursor.execute("""
            ALTER TABLE otp_codes
            ADD COLUMN purpose TEXT NOT NULL DEFAULT 'passwordless_login'
        """)

    # Classes in the school
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER REFERENCES schools(id),
        grade_name TEXT NOT NULL,
        grade_name_kn TEXT NOT NULL,
        section TEXT DEFAULT 'A',
        total_enrolled INTEGER DEFAULT 0,
        boys_enrolled INTEGER DEFAULT 0,
        girls_enrolled INTEGER DEFAULT 0
    );
    """)

    # Students list
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER REFERENCES classes(id),
        roll_no INTEGER NOT NULL,
        name TEXT NOT NULL,
        name_kn TEXT,
        gender TEXT CHECK(gender IN ('M', 'F', 'O')),
        diet_preference TEXT DEFAULT 'egg' CHECK(diet_preference IN ('egg', 'banana', 'chikki')),
        is_active INTEGER DEFAULT 1
    );
    """)

    # Attendance Records (Daily Class-wise summary & total)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER REFERENCES schools(id),
        class_id INTEGER REFERENCES classes(id),
        date TEXT NOT NULL,
        total_present INTEGER NOT NULL,
        boys_present INTEGER NOT NULL,
        girls_present INTEGER NOT NULL,
        marked_by INTEGER REFERENCES users(id),
        status TEXT DEFAULT 'SUBMITTED' CHECK(status IN ('SUBMITTED', 'VERIFIED', 'LOCKED')),
        remarks TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(class_id, date)
    );
    """)

    # Mid-Day Meal Daily Log (PM POSHAN Beneficiaries)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meal_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER REFERENCES schools(id),
        date TEXT UNIQUE NOT NULL,
        beneficiaries_served INTEGER NOT NULL,
        ksheera_bhagya_milk_count INTEGER DEFAULT 0,
        eggs_distributed INTEGER DEFAULT 0,
        bananas_distributed INTEGER DEFAULT 0,
        chikki_distributed INTEGER DEFAULT 0,
        menu_type TEXT NOT NULL,
        menu_type_kn TEXT NOT NULL,
        tasting_score INTEGER DEFAULT 5,
        tasting_notes TEXT,
        tasted_by TEXT,
        logged_by INTEGER REFERENCES users(id),
        status TEXT DEFAULT 'CONFIRMED',
        photo_url TEXT,
        photo_lat REAL,
        photo_lng REAL,
        photo_accuracy REAL,
        photo_timestamp TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Ensure migration columns for meal_records if already created
    try:
        existing_cols = [c[1] for c in cursor.execute("PRAGMA table_info(meal_records)").fetchall()]
        for col_name, col_type in [
            ("photo_url", "TEXT"),
            ("photo_lat", "REAL"),
            ("photo_lng", "REAL"),
            ("photo_accuracy", "REAL"),
            ("photo_timestamp", "TEXT")
        ]:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE meal_records ADD COLUMN {col_name} {col_type}")
    except Exception as e:
        print(f"[DB Migration Warning] meal_records columns check: {e}")

    # Food Inventory Items (Staples, Pulses, Oil, Perishables)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER REFERENCES schools(id),
        item_code TEXT NOT NULL,
        name TEXT NOT NULL,
        name_kn TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('grains', 'pulses', 'oil', 'produce', 'dairy', 'spices')),
        unit TEXT NOT NULL,
        unit_kn TEXT NOT NULL,
        current_stock REAL DEFAULT 0.0,
        min_threshold REAL DEFAULT 5.0,
        norm_per_student_grams REAL DEFAULT 0.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(school_id, item_code)
    );
    """)

    # Inventory Transactions (Stock Inward, Outward Consumption, Adjustments)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER REFERENCES schools(id),
        item_id INTEGER REFERENCES inventory_items(id),
        transaction_type TEXT NOT NULL CHECK(transaction_type IN ('INWARD', 'OUTWARD', 'ADJUSTMENT')),
        quantity REAL NOT NULL,
        balance_after REAL NOT NULL,
        vendor_name TEXT,
        bill_number TEXT,
        cost REAL DEFAULT 0.0,
        notes TEXT,
        date TEXT NOT NULL,
        recorded_by INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Tamper-Evident Audit Trail
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id INTEGER REFERENCES schools(id),
        user_id INTEGER,
        user_name TEXT,
        user_role TEXT,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        ip_address TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
