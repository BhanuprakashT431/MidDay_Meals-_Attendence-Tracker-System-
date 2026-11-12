"""
Firebase & External Integrations Configuration
Provides built-in Firebase initialization, status checks, and client credential distribution.
Supports live Firebase project or smooth local fallback.
"""

import os
import json
from typing import Optional

# Automatically load .env file if present
def _load_local_env():
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".env")),
        ".env"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass
            break

_load_local_env()

# Firebase Client Configuration (Safe for public/frontend exposure)
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY", "AIzaSyCP3dcZ0Hu0j_NbQ_mA9W2Zo2Zk17RDKBI"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "mid-day-meal-project-d475f.firebaseapp.com"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", "mid-day-meal-project-d475f"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "mid-day-meal-project-d475f.firebasestorage.app"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "850056141456"),
    "appId": os.getenv("FIREBASE_APP_ID", "1:850056141456:web:b5deea41534e58c269d615"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", "G-P7JJKTX3RJ")
}

# Meta / Facebook App ID and App Secret configuration
META_CONFIG = {
    "appId": os.getenv("META_APP_ID", "2543235902816325"),
    "appSecret": os.getenv("META_APP_SECRET", "74a94bc85dee2d0da5c1539be31f4d13"),
    "clientToken": os.getenv("META_CLIENT_TOKEN", ""),
    "pixelId": os.getenv("META_PIXEL_ID", "")
}

STITCH_CONFIG = {
    "apiKey": os.getenv("STITCH_API_KEY", ""),
    "projectId": os.getenv("STITCH_PROJECT_ID", "4059288306097933423")
}

def get_public_firebase_config() -> dict:
    """Return the client-safe Firebase configuration."""
    return {
        "configured": bool(FIREBASE_CONFIG.get("apiKey") and FIREBASE_CONFIG.get("projectId")),
        "config": FIREBASE_CONFIG
    }

def get_meta_config() -> dict:
    """Return the client-safe Meta configuration."""
    return {
        "configured": bool(META_CONFIG.get("appId") or META_CONFIG.get("appSecret")),
        "appId": META_CONFIG.get("appId", ""),
        "hasSecret": bool(META_CONFIG.get("appSecret"))
    }

def get_stitch_config() -> dict:
    """Return Stitch configuration status."""
    return {
        "configured": bool(STITCH_CONFIG.get("apiKey")),
        "hasKey": bool(STITCH_CONFIG.get("apiKey"))
    }

def update_runtime_keys(firebase_keys: Optional[dict] = None, meta_keys: Optional[dict] = None, stitch_keys: Optional[dict] = None) -> dict:
    """Update runtime API keys dynamically from admin settings."""
    if firebase_keys:
        for k, v in firebase_keys.items():
            if k in FIREBASE_CONFIG and v:
                FIREBASE_CONFIG[k] = v.strip()
    if meta_keys:
        for k, v in meta_keys.items():
            if k in META_CONFIG and v:
                META_CONFIG[k] = v.strip()
    if stitch_keys:
        for k, v in stitch_keys.items():
            if k in STITCH_CONFIG and v:
                STITCH_CONFIG[k] = v.strip()

    return {
        "firebase": get_public_firebase_config(),
        "meta": get_meta_config(),
        "stitch": get_stitch_config()
    }
