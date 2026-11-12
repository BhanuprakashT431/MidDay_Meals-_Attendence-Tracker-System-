# 🍱 Smart-Nourish & Attend: Digital Mid-Day Meal and Attendance Management System
### ಕರ್ನಾಟಕ ಸರ್ಕಾರ ಶಾಲಾ ಶಿಕ್ಷಣ ಮತ್ತು ಸಾಕ್ಷರತಾ ಇಲಾಖೆ (PM-POSHAN / ಅಕ್ಷರ ದಾಸೋಹ ಯೋಜನೆ)
**Client Deployment Mode (Zero Mock Data) • Karnataka Educational Institutions**  
*Ref: PM-POSHAN Institutional Digitization Platform*

---

## 🌟 Executive Overview
**Smart-Nourish & Attend** is a state-of-the-art, secure, mobile-first Progressive Web Application (PWA) and backend API built specifically for government schools in Karnataka. It digitizes student attendance and mid-day meal operations (PM-POSHAN / Akshara Dasoha), eliminating paper registers, manual arithmetic errors, and inventory discrepancy while strengthening institutional transparency and audit compliance.

---

## 🚀 Key Capabilities & Features

### 1. 🌐 Full Bilingual Interface: Kannada (ಕನ್ನಡ) & English (EN)
- **100% Bilingual localization**: Seamless toggle between authentic Kannada and English across every dashboard card, form, unit, alert, table, and report.
- Persistent user language preference saved in local storage.

### 2. 🔐 Enterprise-Grade Server Security & Authentication
- **Secure Email OTP Login**: Generates cryptographically secure 6-digit OTPs with salted SHA-256 hashes, 5-minute expiry, and brute-force lockout (max 3 attempts).
- **Password Authentication**: Bcrypt hashing with cryptographic salt rounds.
- **JWT (JSON Web Tokens)**: Stateles signed tokens containing role-based authorization scopes.
- **Role-Based Access Control (RBAC)**:
  - 👑 **Head Master (ಮುಖ್ಯೋಪಾಧ್ಯಾಯರು)**: Comprehensive oversight, record locking, staff management, audit trail inspection, and monthly compliance sign-off.
  - 📘 **Teachers (ಶಿಕ್ಷಕರು)**: Class-wise student attendance entry, meal beneficiary logging, food quality tasting verification.
  - 🍲 **Kitchen Staff / Cooks (ಅಡುಗೆ ಸಿಬ್ಬಂದಿ)**: Ration delivery receipt, fresh vegetable logging, daily kitchen consumption views.
- **Tamper-Evident Audit Trail**: Every sensitive state change (attendance submission, meal count, ration receipt, inventory deduction) is permanently logged with timestamps, user IDs, roles, and client IP addresses.

### 3. 📱 Mobile-First Native Experience & Offline Capability (2G/3G Ready)
- Designed to run smoothly in rural and semi-urban schools with weak or intermittent connectivity.
- **Offline Request Queue**: If a teacher marks attendance or logs meals without internet, changes are queued locally and automatically synced with the server once connectivity is restored.
- **Progressive Web App (PWA)**: Installable directly onto Android and iOS home screens with zero app store overhead.

### 4. 🍛 Mid-Day Meal Tracking & Automated Ration Calculations
- Enforces data integrity: **Meal beneficiaries served cannot exceed marked student attendance**.
- **Automated Stock Deduction**: Calculates consumption automatically based on official Karnataka PM-POSHAN High School per-child weight norms:
  - 🌾 **Rice (ಅಕ್ಕಿ)**: 150 grams per student
  - 🍲 **Tur Dal (ತೊಗರಿ ಬೇಳೆ)**: 30 grams per student
  - 🌻 **Cooking Oil (ಅಡುಗೆ ಎಣ್ಣೆ)**: 7.5 ml/grams per student
  - 🥕 **Fresh Vegetables (ತರಕಾರಿಗಳು)**: 75 grams per student
  - 🧂 **Salt (ಉಪ್ಪು)**: 4 grams per student
  - 🥛 **Ksheera Bhagya Milk (ಹಾಲು)**: 15 grams milk powder (150 ml) per child
  - 🥚 **Eggs / Bananas / Chikki**: 1:1 distribution tracking
- **Mandatory Tasting & Hygiene Log**: Head Master or assigned teacher tastes the food 30 minutes before serving, records 1-5 star hygiene rating, and logs observation notes.

### 5. 📦 Food Inventory & Perishable Fresh Produce Ledger
- Tracks staple rations, pulses, cooking oil, and market produce.
- **Stock Inward**: Bill number, vendor details, received quantities, and purchase cost.
- **Fresh Produce**: Logging of local market vegetables (tomato, potato, beans, spinach, etc.).
- **Real-Time Balance & Safety Alerts**: Visual indicators and warning banners when stocks drop below 5 school days of consumption.

### 6. 📊 Official Monthly Compliance Reports (BEO Format)
- Consolidated monthly summaries formatted for submission to the Block Education Officer (BEO) and Akshara Dasoha Taluk Office.
- Print-friendly layout for physical archiving and administrative sign-off.

---

## 📂 Project Architecture

```
Mid Day Meal/
├── backend/
│   ├── app.py                 # FastAPI application, REST endpoints, RBAC middleware, PWA serving
│   ├── security.py            # Bcrypt, JWT tokens, secure OTP generation, rate limiting
│   ├── email_service.py       # Email OTP delivery (SMTP support + Developer Simulator)
│   ├── firebase_config.py     # Inbuilt Firebase, Stitch, and Meta runtime configurations
│   ├── models.py              # Pydantic schemas and input sanitization
│   └── database.py            # SQLite database with clean relational schema (0 mock rows)
├── frontend/
│   ├── index.html             # Mobile-first app frame, meta tags, and responsive screens
│   ├── manifest.json          # PWA manifest for Android and iOS Add to Home Screen
│   ├── sw.js                  # Service Worker for offline caching
│   ├── css/
│   │   └── style.css          # Design system with glassmorphism & Karnataka heritage palette
│   ├── js/
│   │   ├── i18n.js            # Bilingual Kannada & English dictionary and translation engine
│   │   ├── api.js             # API client with JWT, offline queue, and auto-sync
│   │   ├── app.js             # Navigation, real-time ration calculation preview, forms
│   │   ├── charts.js          # Lightweight SVG charts for attendance gauge and stock levels
│   │   └── firebase-init.js   # Dynamic Firebase SDK bootstrap and fallback handler
│   └── assets/
│       └── logo.svg           # Karnataka School Mid-Day Meal emblem
├── .env.example               # Environment variables template
├── run_server.py              # Local server launcher
└── README.md                  # System documentation and deployment guide
```

---

## ⚡ Quick Start (Running Locally)

### 1. Launch the Server
From the project folder, run:
```powershell
python run_server.py
```

### 2. Access the Application
- **Mobile Web App**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Redoc API Reference**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Institution Onboarding & Setup Flow
When launching the application for a new client:
1. Open [http://localhost:8000/](http://localhost:8000/)
2. On the login screen, click **"Register New School & Administrator"**.
3. Enter the school's **11-digit DISE Code**, **School Name**, **Taluk**, **District**, and **Head Master / Admin credentials**.
4. Upon submission, the school profile, classes, and official Karnataka PM-POSHAN inventory categories are provisioned with 0 mock rows, ready for real student and stock records.

---

## 🔑 Integrating API Keys (Firebase, Stitch, Meta)

You can provide your API keys in two convenient ways:

### Method 1: Using the In-App Settings Modal (Instant Runtime Update)
1. Open the app in your browser at `http://localhost:8000/`.
2. Tap the **⚙️ (Settings)** icon in the top header.
3. Paste your **Firebase API Key & Project ID**, **Stitch API Key**, or **Meta App ID**.
4. Tap **Save Keys**. The system will immediately activate the integrations.

### Method 2: Via `.env` File (Persistent Environment Setup)
Copy `.env.example` to `.env` and fill in your values:
```env
# Server Security
JWT_SECRET_KEY=your-secure-random-jwt-key
PORT=8000

# Firebase Credentials
FIREBASE_API_KEY=AIzaSy...
FIREBASE_AUTH_DOMAIN=midday-meal-karnataka.firebaseapp.com
FIREBASE_PROJECT_ID=midday-meal-karnataka
FIREBASE_STORAGE_BUCKET=midday-meal-karnataka.appspot.com
FIREBASE_MESSAGING_SENDER_ID=...
FIREBASE_APP_ID=...

# Stitch API Key (from your Stitch prototype project)
STITCH_API_KEY=...
STITCH_PROJECT_ID=...

# Meta / Facebook App ID
META_APP_ID=...

# Production SMTP Email (for real email OTP dispatch via Gmail / AWS SES)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-school-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=noreply@middaymeal.karnataka.gov.in
```

---

## 🌐 Complete Guide Until Deployment

### Option A: Free Cloud Deployment (Render / Railway / Fly.io)
1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial Smart-Nourish release"
   git branch -M main
   git remote add origin https://github.com/your-username/karnataka-midday-meal.git
   git push -u origin main
   ```
2. **Deploy on Render.com**:
   - Create a **New Web Service** and link your GitHub repository.
   - Environment: `Python 3`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `python run_server.py`
   - Under **Environment Variables**, add the keys from `.env`.
3. Your application will be live with a free SSL/HTTPS URL (`https://your-app.onrender.com`).

### Option B: Mobile App Packaging for Android & iOS (Google Play Store)
You can package this PWA into a native Android APK or AAB file using:

1. **Bubblewrap / Trusted Web Activity (TWA)** (Recommended for Google Play Store):
   ```bash
   npx @bubblewrap/cli init --manifest=https://your-app.onrender.com/manifest.json
   npx @bubblewrap/cli build
   ```
   This generates a signed Android `.apk` and `.aab` file ready for the Google Play Console!

2. **CapacitorJS (Native Shell with Camera / Barcode Support)**:
   ```bash
   npm init @capacitor/app
   npx cap add android
   npx cap open android
   ```

### Option C: Direct PWA Install on Mobile (Zero Cost)
- Open the application URL in Google Chrome (Android) or Safari (iOS).
- Tap the browser menu `⋮` and select **"Add to Home Screen"** / **"Install App"**.
- The app will install with its native icon, launch in standalone fullscreen mode, and provide offline access.

---

## 🏛️ Government Compliance & Acknowledgement
This system has been architected to adhere to the operational guidelines set forth by:
- **PM-POSHAN Scheme (Pradhan Mantri Poshan Shakti Nirman)**
- **Department of School Education & Literacy, Government of Karnataka**
- **Unified District Information System for Education (UDISE+) Data Standards**
