"""
Smart-Nourish & Attend: Digital Mid-Day Meal and Attendance Management System
Server Startup & Development Launcher
"""

import os
import sys

# Configure UTF-8 stdout on Windows to prevent UnicodeEncodeError
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

import socket
import uvicorn
from database import init_db

def get_lan_ip():
    """Detect the local Wi-Fi / LAN IP address of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    print("\n" + "=" * 68)
    print("  SMART-NOURISH & ATTEND: KARNATAKA MID-DAY MEAL SYSTEM")
    print("  Dual-Device Access Mode (Desktop PC & Mobile Phone)")
    print("=" * 68)

    # Initialize DB
    init_db()
    print("[DB] SQLite database initialized with clean tables.")

    port = int(os.getenv("PORT", "8000"))
    host = "0.0.0.0"
    lan_ip = get_lan_ip()

    print(f"\n  [PC Access]     Open in PC Browser:    http://localhost:{port}/")
    print(f"  [Phone Access]  Open on Mobile Phone:  http://{lan_ip}:{port}/")
    print(f"                  *(Make sure phone is connected to the same Wi-Fi)*")
    print(f"\n  [API Docs]      Swagger Documentation: http://localhost:{port}/docs")
    print("=" * 68 + "\n")

    uvicorn.run("app:app", host=host, port=port, reload=False, app_dir=BACKEND_DIR)

