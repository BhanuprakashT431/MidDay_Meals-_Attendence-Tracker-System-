/**
 * Internationalization (i18n) Engine
 * Full Bilingual Support: Kannada (ಕನ್ನಡ) & English (EN)
 * Covers 100% of screens, forms, alerts, and system reports.
 */

const translations = {
  en: {
    // Branding & Header
    app_title: "Smart-Nourish & Attend",
    app_subtitle: "Digital Mid-Day Meal & Attendance Management",
    school_name_default: "Karnataka PM-POSHAN School Portal",
    taluk_district: "Department of School Education & Literacy, Karnataka",
    pm_poshan: "PM POSHAN / Akshara Dasoha Scheme",
    academic_cycle: "Academic Cycle 2024–25 Active",
    hero_headline_1: "Nourishing Young Minds, Empowering",
    hero_headline_2: "Educators",
    hero_subtitle: "Unified digital attendance & Mid-Day Meal daily ration allocation for government primary & upper primary schools nationwide.",
    daily_meals_logged: "1,248,390 Meals Logged",
    core_pillars_title: "Core Pillars for Educators",
    pillar_1_title: "60-Second Roll Call",
    pillar_1_desc: "Mark classes in seconds with smart auto-present toggles, cached class registers, and geo-stamped local logging.",
    pillar_2_title: "Automated MDM Ration Calculators",
    pillar_2_desc: "Calculates exact daily rice, dal, and fortified oil measures instantly matching attendance rolls against sanctioned quota.",
    pillar_3_title: "Leak-Proof Transparent Rations",
    pillar_3_desc: "End-to-end reconciliation prevents stock discrepancies and issues automated alerts before food buffers drop.",
    sso_title: "Single Sign-On Access",
    sso_subtitle: "UDISE+ Linked Verification",
    sso_desc: "Teachers, Headmasters, and Cluster Resource Coordinators (CRC) can access registers with registered mobile OTP or UDISE PIN.",
    btn_login_portal: "Headmaster Login",
    btn_register_terminal: "Register School & Headmaster",
    btn_guest_demo: "Explore Guest Demo Mode",
    modal_login_title: "Headmaster Portal Login",
    btn_firebase_google: "Sign in with Google (Firebase)",
    btn_meta_login: "Continue with Meta",
    or_school_credentials: "or Headmaster credentials",
    biometric_login: "Biometric / Aadhaar Iris Login",
    national_helpline: "National Shiksha Helpline",
    email_or_mobile: "Official Email / Mobile",
    otp_dispatch_hint: "A 6-digit secure verification code will be dispatched.",

    // Navigation
    nav_dashboard: "Dashboard",
    nav_attendance: "Attendance",
    nav_meals: "Mid-Day Meal",
    nav_inventory: "Stock & Produce",
    nav_reports: "Reports & Audit",

    // Auth & Roles
    login_title: "School Personnel Login",
    login_subtitle: "Access official mid-day meal & attendance portal",
    tab_otp_login: "Login with OTP",
    tab_password_login: "Login with Password",
    tab_register: "Register Staff",
    email_label: "Official Email Address",
    email_placeholder: "e.g. staff@school.gov.in",
    password_label: "Password",
    password_placeholder: "Enter your password",
    otp_label: "Enter 6-Digit Email OTP",
    otp_placeholder: "6-digit OTP code",
    btn_request_otp: "Send Login OTP",
    btn_resend_otp: "Resend OTP",
    btn_verify_otp: "Verify & Enter",
    btn_login_password: "Sign In Securely",
    btn_register: "Register Account",
    full_name_label: "Full Name",
    full_name_placeholder: "Enter full name",
    phone_label: "Mobile Number",
    phone_placeholder: "10-digit mobile number",
    dise_code_label: "School DISE Code",
    dise_code_placeholder: "Enter school DISE code",
    role_label: "Designation / Role",
    role_hm: "Head Master (ಮುಖ್ಯೋಪಾಧ್ಯಾಯರು)",
    role_teacher: "Teacher (ಶಿಕ್ಷಕರು)",
    role_cook: "Kitchen Staff / Cook (ಅಡುಗೆ ಸಿಬ್ಬಂದಿ)",
    role_admin: "System Administrator",
    logout: "Sign Out",
    quick_test_accounts: "Quick Demo Logins (Click to autofill):",

    // Dashboard
    dash_today_summary: "Today's School Summary",
    dash_total_enrolled: "Total Enrolled",
    dash_today_present: "Students Present",
    dash_meals_served: "Meals Served Today",
    dash_milk_served: "Ksheera Bhagya Milk",
    dash_eggs_served: "Eggs / Bananas",
    dash_attendance_rate: "Attendance Rate",
    dash_quick_actions: "Quick School Actions",
    action_mark_attendance: "Mark Attendance",
    action_log_meal: "Log Today's Meal",
    action_add_stock: "Add Stock / Produce",
    action_view_reports: "Generate Monthly Report",
    dash_stock_health: "Critical Stock Status",
    stock_balance: "Current Stock",
    days_left: "days remaining",
    low_stock_warning: "LOW STOCK WARNING",
    stock_sufficient: "Stock Sufficient",

    // Attendance
    att_title: "Daily Student Attendance",
    att_subtitle: "Class-wise attendance recording and verification",
    select_date: "Select Date",
    mark_all_present: "Mark All Present",
    class_name: "Class",
    section: "Section",
    enrolled_boys: "Boys Enrolled",
    enrolled_girls: "Girls Enrolled",
    present_boys: "Boys Present",
    present_girls: "Girls Present",
    class_total: "Class Total",
    att_remarks: "Remarks / Verification Note",
    btn_save_attendance: "Submit Attendance Record",
    att_locked_note: "Head Master verified and locked.",

    // Mid-Day Meal Log
    meal_title: "Daily Mid-Day Meal (PM-POSHAN) Tracking",
    meal_subtitle: "Record beneficiaries, menu, quality tasting, and auto-deduct stock",
    meal_date: "Meal Date",
    beneficiaries_count: "Total Beneficiaries (Students Fed)",
    beneficiaries_helper: "Cannot exceed marked attendance for the day",
    today_menu: "Today's Meal Menu",
    menu_rice_sambar: "Rice, Sambar & Fresh Leafy Vegetables (ಅನ್ನ, ಸಾಂಬಾರ್, ಸೊಪ್ಪು)",
    menu_bisi_bele_bath: "Bisi Bele Bath & Boiled Egg (ಬಿಸಿಬೇಳೆ ಬಾತ್, ಮೊಟ್ಟೆ)",
    menu_chitranna: "Lemon Rice (Chitranna) & Vegetable Upma (ಚಿತ್ರಾನ್ನ, ತರಕಾರಿ ಉಪ್ಪಿಟ್ಟು)",
    menu_special: "Special Festival Meal (ವಿಶೇಷ ಹಬ್ಬದ ಊಟ)",
    ksheera_bhagya: "Ksheera Bhagya Milk (Servings)",
    eggs_count: "Boiled Eggs Distributed",
    bananas_count: "Bananas Distributed (Vegetarian / Opted)",
    chikki_count: "Peanut Chikki Distributed",
    tasting_section_title: "Mandatory Meal Quality & Tasting Log",
    tasting_helper: "Must be tasted 30 mins before serving by HM / Teacher / Cook",
    tasting_rating: "Quality & Hygiene Rating",
    tasting_notes: "Taste, Freshness & Hygiene Observation",
    tasting_notes_placeholder: "e.g. Rice well cooked, sambar appropriately spiced, vegetables fresh.",
    tasted_by: "Tasted & Approved By",
    tasted_by_placeholder: "e.g. Head Master / Designated Teacher",
    auto_deduction_preview: "Automatic PM-POSHAN Ration Deduction Preview:",
    btn_save_meal: "Save Meal Record & Deduct Inventory",
    geotag_plate: "Geotagged Plate Verification",
    capture_meal_plate: "Capture Today's Meal Plate Photo",
    capture_gps_hint: "Opens camera with real-time GPS coordinate & timestamp watermark",
    take_plate_photo: "Take Geotagged Photo",
    retake_photo: "Retake Photo",
    gps_calibrating: "Calibrating GPS...",
    gps_calibrated: "GPS Calibrated",
    gps_locked: "GPS Locked",
    accuracy_meters: "Accuracy",
    cook_duty_title: "Cook-cum-Helper Duty Log",
    on_duty: "On Duty",
    on_leave: "On Leave",
    cook_head_title: "Head Cook",
    cook_assistant_title: "Assistant Cook",
    cook_shift_1: "Morning Shift • Meal Preparation",
    cook_shift_2: "Sanitation & Serving",
    cook_present_count: "Present",

    // Inventory & Produce
    inv_title: "Inventory & Fresh Produce Ledger",
    inv_subtitle: "Track staple grains, pulses, cooking oil and perishable market produce",
    tab_inventory_status: "Stock Overview",
    tab_stock_inward: "Stock Inward Receipt",
    tab_fresh_produce: "Fresh Produce Purchase",
    tab_transactions: "Transaction History",
    item_name: "Item Name",
    category: "Category",
    current_quantity: "Available Quantity",
    unit: "Unit",
    threshold: "Safety Threshold",
    status_col: "Status",
    receipt_date: "Receipt Date",
    select_item: "Select Food Item",
    quantity_received: "Quantity Received",
    vendor_name: "Supplier / Shop Name",
    bill_number: "Bill / Invoice Number",
    total_cost: "Total Cost (Rs.)",
    produce_name: "Vegetable / Fruit Name",
    produce_name_placeholder: "e.g. Tomato, Potato, Beans, Spinach (ತೊಗರಿ ಸೊಪ್ಪು)",
    produce_name_kn: "Name in Kannada",
    produce_kg: "Quantity in Kilograms (KG)",
    btn_submit_inward: "Save Inward Stock",
    btn_submit_produce: "Record Produce Entry",

    // Reports & Compliance
    rep_title: "Monthly Compliance & Audit Reports",
    rep_subtitle: "Karnataka Department of School Education Official Format",
    select_month: "Select Reporting Month",
    total_working_days: "Total Working Days",
    total_meals_month: "Total Meals Served in Month",
    avg_beneficiaries: "Average Daily Beneficiaries",
    total_milk_month: "Total Ksheera Bhagya Milk Cups",
    total_eggs_month: "Total Eggs Distributed",
    consumption_summary: "Stock Consumption Summary",
    receipt_summary: "Stock Inward Summary",
    item_consumed: "Consumed",
    item_received: "Received",
    btn_export_pdf: "Print / Export Compliance PDF",

    // Audit Trail
    audit_title: "Tamper-Evident Security Audit Log",
    audit_subtitle: "Traceable records of every entry, modification, and user action",
    audit_timestamp: "Timestamp",
    audit_user: "User",
    audit_role: "Role",
    audit_action: "Action",
    audit_details: "Details",
    audit_ip: "IP Address",

    // Cloud & Settings Modal
    settings_title: "Cloud Integrations & API Keys",
    settings_subtitle: "Configure Firebase, Stitch API, and Meta tokens",
    firebase_status: "Firebase Status",
    stitch_status: "Stitch Integration Status",
    meta_status: "Meta (Facebook) App Status",
    input_firebase_key: "Firebase API Key",
    input_firebase_project: "Firebase Project ID",
    input_stitch_key: "Stitch API Key",
    input_meta_app_id: "Meta App ID",
    btn_save_keys: "Update Runtime API Keys",
    keys_saved_success: "API Keys configured and saved successfully.",

    // Alerts & Notifications
    alert_offline: "You are currently offline. Changes will sync when network connects.",
    alert_online: "Internet connection restored. Synchronized with server.",
    alert_success: "Action completed successfully!",
    alert_error: "An error occurred. Please check and retry.",
    offline_badge: "Offline Mode (2G/3G Ready)",
    online_badge: "Live Server Connected"
  },

  kn: {
    // Branding & Header
    app_title: "ಸ್ಮಾರ್ಟ್ ಪೋಷಣ್ & ಹಾಜರಾತಿ",
    app_subtitle: "ಡಿಜಿಟಲ್ ಮಧ್ಯಾಹ್ನದ ಊಟ ಮತ್ತು ಹಾಜರಾತಿ ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ",
    school_name_default: "ಕರ್ನಾಟಕ ಪಿಎಂ-ಪೋಷಣ್ ಶಾಲಾ ಪೋರ್ಟಲ್",
    taluk_district: "ಶಾಲಾ ಶಿಕ್ಷಣ ಮತ್ತು ಸಾಕ್ಷರತಾ ಇಲಾಖೆ, ಕರ್ನಾಟಕ",
    pm_poshan: "ಪಿ.ಎಂ. ಪೋಷಣ್ / ಅಕ್ಷರ ದಾಸೋಹ ಯೋಜನೆ",
    academic_cycle: "ಶೈಕ್ಷಣಿಕ ವರ್ಷ ೨೦೨೪–೨೫ ಸಕ್ರಿಯ",
    hero_headline_1: "ಚಿಕ್ಕ ಮನಸ್ಸುಗಳಿಗೆ ಪೋಷಣೆ, ಶಿಕ್ಷಕರಿಗೆ",
    hero_headline_2: "ಸಬಲೀಕರಣ",
    hero_subtitle: "ಸರ್ಕಾರಿ ಪ್ರಾಥಮಿಕ ಮತ್ತು ಪ್ರೌಢಶಾಲೆಗಳಿಗೆ ಡಿಜಿಟಲ್ ಹಾಜರಾತಿ ಮತ್ತು ಬಿಸಿಯೂಟ ಪಡಿತರ ನಿರ್ವಹಣೆ.",
    daily_meals_logged: "೧೨,೪೮,೩೯೦ ಊಟ ದಾಖಲಿಸಲಾಗಿದೆ",
    core_pillars_title: "ಶಿಕ್ಷಕರ ಪ್ರಮುಖ ಸೌಲಭ್ಯಗಳು",
    pillar_1_title: "೬೦ ಸೆಕೆಂಡುಗಳ ಹಾಜರಾತಿ",
    pillar_1_desc: "ಸ್ಮಾರ್ಟ್ ಹಾಜರಾತಿ ಟಾಗಲ್ ಮತ್ತು ಸ್ಥಳೀಯ ನಮೂದು ಮೂಲಕ ಕ್ಷಣಾರ್ಧದಲ್ಲಿ ಹಾಜರಾತಿ ದಾಖಲಿಸಿ.",
    pillar_2_title: "ಸ್ವಯಂಚಾಲಿತ ಪಡಿತರ ಲೆಕ್ಕಾಚಾರ",
    pillar_2_desc: "ಹಾಜರಾತಿಗೆ ಅನುಗುಣವಾಗಿ ದೈನಂದಿನ ಅಕ್ಕಿ, ಬೇಳೆ ಮತ್ತು ಎಣ್ಣೆಯ ಪ್ರಮಾಣವನ್ನು ತಕ್ಷಣ ಲೆಕ್ಕಹಾಕುತ್ತದೆ.",
    pillar_3_title: "ಪಾರದರ್ಶಕ ಆಹಾರ ದಾಸ್ತಾನು",
    pillar_3_desc: "ದಾಸ್ತಾನು ಕೊರತೆಯಾಗದಂತೆ ಮುನ್ಸೂಚನೆ ಮತ್ತು ಪಾರದರ್ಶಕ ದಾಸ್ತಾನು ನಿರ್ವಹಣೆ.",
    sso_title: "ಏಕೀಕೃತ ಪ್ರವೇಶ (SSO)",
    sso_subtitle: "UDISE+ ಲಿಂಕ್ ಪರಿಶೀಲನೆ",
    sso_desc: "ಶಿಕ್ಷಕರು, ಮುಖ್ಯೋಪಾಧ್ಯಾಯರು ಮತ್ತು ಸಿ.ಆರ್.ಸಿ ಅಧಿಕಾರಿಗಳು ಮೊಬೈಲ್ ಒಟಿಪಿ ಅಥವಾ ಯುಡೈಸ್ ಪಿನ್ ಮೂಲಕ ಲಾಗಿನ್ ಆಗಬಹುದು.",
    btn_login_portal: "ಮುಖ್ಯೋಪಾಧ್ಯಾಯರ ಲಾಗಿನ್",
    btn_register_terminal: "ಶಾಲಾ ಮತ್ತು ಮುಖ್ಯೋಪಾಧ್ಯಾಯರ ನೋಂದಣಿ",
    btn_guest_demo: "ಅತಿಥಿ ಡೆಮೊ ಮೋಡ್ ಅನ್ವೇಷಿಸಿ",
    modal_login_title: "ಮುಖ್ಯೋಪಾಧ್ಯಾಯರ ಪೋರ್ಟಲ್ ಲಾಗಿನ್",
    btn_firebase_google: "ಗೂಗಲ್ ಮೂಲಕ ಲಾಗಿನ್ (Firebase)",
    btn_meta_login: "ಮೆಟಾ ಮೂಲಕ ಮುಂದುವರಿಯಿರಿ",
    or_school_credentials: "ಅಥವಾ ಮುಖ್ಯೋಪಾಧ್ಯಾಯರ ಲಾಗಿನ್ ವಿವರ ಬಳಸಿ",
    biometric_login: "ಬಯೋಮೆಟ್ರಿಕ್ / ಆಧಾರ್ ಲಾಗಿನ್",
    national_helpline: "ರಾಷ್ಟ್ರೀಯ ಶಿಕ್ಷಣ ಸಹಾಯವಾಣಿ",
    email_or_mobile: "ಅಧಿಕೃತ ಇಮೇಲ್ / ಮೊಬೈಲ್",
    otp_dispatch_hint: "೬-ಅಂಕಿಯ ಸುರಕ್ಷಿತ ಪರಿಶೀಲನಾ ಕೋಡ್ ಕಳುಹಿಸಲಾಗುವುದು.",

    // Navigation
    nav_dashboard: "ಮುಖಪುಟ",
    nav_attendance: "ಹಾಜರಾತಿ",
    nav_meals: "ಮಧ್ಯಾಹ್ನದ ಊಟ",
    nav_inventory: "ದಾಸ್ತಾನು ಲೆಕ್ಕ",
    nav_reports: "ವರದಿಗಳು",

    // Auth & Roles
    login_title: "ಶಾಲಾ ಸಿಬ್ಬಂದಿ ಲಾಗಿನ್",
    login_subtitle: "ಅಕ್ಷರ ದಾಸೋಹ ಮತ್ತು ಹಾಜರಾತಿ ಅಧಿಕೃತ ಪೋರ್ಟಲ್",
    tab_otp_login: "ಒಟಿಪಿ ಮೂಲಕ ಲಾಗಿನ್",
    tab_password_login: "ಪಾಸ್‌ವರ್ಡ್ ಲಾಗಿನ್",
    tab_register: "ಹೊಸ ಸಿಬ್ಬಂದಿ ನೋಂದಣಿ",
    email_label: "ಅಧಿಕೃತ ಇಮೇಲ್ ವಿಳಾಸ",
    email_placeholder: "ಉದಾ: staff@school.gov.in",
    password_label: "ಪಾಸ್‌ವರ್ಡ್",
    password_placeholder: "ನಿಮ್ಮ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ",
    otp_label: "ಇಮೇಲ್ ಒಟಿಪಿ ನಮೂದಿಸಿ",
    otp_placeholder: "೬ ಅಂಕಿಯ ಒಟಿಪಿ ಕೋಡ್",
    btn_request_otp: "ಒಟಿಪಿ ಕಳುಹಿಸಿ",
    btn_resend_otp: "ಮತ್ತೆ ಒಟಿಪಿ ಕಳುಹಿಸಿ",
    btn_verify_otp: "ಪರಿಶೀಲಿಸಿ ಪ್ರವೇಶಿಸಿ",
    btn_login_password: "ಸುರಕ್ಷಿತವಾಗಿ ಪ್ರವೇಶಿಸಿ",
    btn_register: "ಖಾತೆ ನೋಂದಾಯಿಸಿ",
    full_name_label: "ಪೂರ್ಣ ಹೆಸರು",
    full_name_placeholder: "ಪೂರ್ಣ ಹೆಸರು ನಮೂದಿಸಿ",
    phone_label: "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ",
    phone_placeholder: "೧೦ ಅಂಕಿಯ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ",
    dise_code_label: "ಶಾಲಾ ಡೈಸ್ (DISE) ಕೋಡ್",
    dise_code_placeholder: "ಡೈಸ್ ಕೋಡ್ ನಮೂದಿಸಿ",
    role_label: "ಹುದ್ದೆ / ಪಾತ್ರ",
    role_hm: "ಮುಖ್ಯೋಪಾಧ್ಯಾಯರು (HM)",
    role_teacher: "ಶಿಕ್ಷಕರು (Teacher)",
    role_cook: "ಅಡುಗೆ ಸಿಬ್ಬಂದಿ (Cook)",
    role_admin: "ವ್ಯವಸ್ಥಾಪಕರು (Admin)",
    logout: "ನಿರ್ಗಮಿಸಿ (Logout)",
    quick_test_accounts: "ಡೆಮೊ ಲಾಗಿನ್ (ಆಯ್ಕೆ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ):",

    // Dashboard
    dash_today_summary: "ಇಂದಿನ ಶಾಲಾ ವಿವರ ಸಾರಾಂಶ",
    dash_total_enrolled: "ಒಟ್ಟು ದಾಖಲಾತಿ",
    dash_today_present: "ಇಂದಿನ ಹಾಜರಾತಿ",
    dash_meals_served: "ಊಟ ಸವಿದ ಮಕ್ಕಳು",
    dash_milk_served: "ಕ್ಷೀರಭಾಗ್ಯ ಹಾಲು",
    dash_eggs_served: "ಮೊಟ್ಟೆ / ಬಾಳೆಹಣ್ಣು",
    dash_attendance_rate: "ಹಾಜರಾತಿ ಶೇಕಡಾವಾರು",
    dash_quick_actions: "ತ್ವರಿತ ಕಾರ್ಯಗಳು",
    action_mark_attendance: "ಹಾಜರಾತಿ ನಮೂದಿಸಿ",
    action_log_meal: "ಇಂದಿನ ಊಟದ ವಿವರ",
    action_add_stock: "ದಾಸ್ತಾನು / ತರಕಾರಿ ಸೇರಿಸಿ",
    action_view_reports: "ಮಾಸಿಕ ವರದಿ ತಯಾರಿಸಿ",
    dash_stock_health: "ಮುಖ್ಯ ದಾಸ್ತಾನು ಸ್ಥಿತಿ",
    stock_balance: "ಪ್ರಸ್ತುತ ದಾಸ್ತಾನು",
    days_left: "ದಿನಗಳ ದಾಸ್ತಾನು ಉಳಿದಿದೆ",
    low_stock_warning: "ಕಡಿಮೆ ದಾಸ್ತಾನು ಎಚ್ಚರಿಕೆ",
    stock_sufficient: "ದಾಸ್ತಾನು ಸಮರ್ಪಕವಾಗಿದೆ",

    // Attendance
    att_title: "ದೈನಂದಿನ ವಿದ್ಯಾರ್ಥಿ ಹಾಜರಾತಿ",
    att_subtitle: "ತರಗತಿವಾರು ಹಾಜರಾತಿ ನಮೂದು ಮತ್ತು ಪರಿಶೀಲನೆ",
    select_date: "ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ",
    mark_all_present: "ಎಲ್ಲರೂ ಹಾಜರು",
    class_name: "ತರಗತಿ",
    section: "ವಿಭಾಗ",
    enrolled_boys: "ದಾಖಲಾದ ಹುಡುಗರು",
    enrolled_girls: "ದಾಖಲಾದ ಹುಡುಗಿಯರು",
    present_boys: "ಹಾಜರಾದ ಹುಡುಗರು",
    present_girls: "ಹಾಜರಾದ ಹುಡುಗಿಯರು",
    class_total: "ತರಗತಿಯ ಒಟ್ಟು",
    att_remarks: "ಟಿಪ್ಪಣಿ / ಪರಿಶೀಲನಾ ವಿವರ",
    btn_save_attendance: "ಹಾಜರಾತಿ ದಾಖಲೆಯನ್ನು ಉಳಿಸಿ",
    att_locked_note: "ಮುಖ್ಯೋಪಾಧ್ಯಾಯರಿಂದ ಪರಿಶೀಲಿಸಿ ಲಾಕ್ ಮಾಡಲಾಗಿದೆ.",

    // Mid-Day Meal Log
    meal_title: "ದೈನಂದಿನ ಮಧ್ಯಾಹ್ನದ ಊಟ (ಅಕ್ಷರ ದಾಸೋಹ) ವಿವರ",
    meal_subtitle: "ಫಲಾನುಭವಿಗಳ ಸಂಖ್ಯೆ, ಆಹಾರ ಪರೀಕ್ಷೆ ಮತ್ತು ಸ್ವಯಂಚಾಲಿತ ದಾಸ್ತಾನು ಕಡಿತ",
    meal_date: "ಊಟದ ದಿನಾಂಕ",
    beneficiaries_count: "ಊಟ ಪಡೆದ ವಿದ್ಯಾರ್ಥಿಗಳ ಸಂಖ್ಯೆ",
    beneficiaries_helper: "ಇಂದಿನ ಹಾಜರಾತಿಗಿಂತ ಹೆಚ್ಚು ಇರಬಾರದು",
    today_menu: "ಇಂದಿನ ಊಟದ ಮೆನು",
    menu_rice_sambar: "ಅನ್ನ, ತರಕಾರಿ ಸಾಂಬಾರ್, ಸೊಪ್ಪು",
    menu_bisi_bele_bath: "ಬಿಸಿಬೇಳೆ ಬಾತ್, ಮೊಟ್ಟೆ / ಬಾಳೆಹಣ್ಣು",
    menu_chitranna: "ಚಿತ್ರಾನ್ನ, ತರಕಾರಿ ಉಪ್ಪಿಟ್ಟು",
    menu_special: "ವಿಶೇಷ ಹಬ್ಬದ ಊಟ",
    ksheera_bhagya: "ಕ್ಷೀರಭಾಗ್ಯ ಹಾಲು (ಸಂಖ್ಯೆ)",
    eggs_count: "ಮೊಟ್ಟೆ ವಿತರಣೆ ಸಂಖ್ಯೆ",
    bananas_count: "ಬಾಳೆಹಣ್ಣು ವಿತರಣೆ ಸಂಖ್ಯೆ",
    chikki_count: "ಕಡಲೆಕಾಯಿ ಚಿಕ್ಕಿ ವಿತರಣೆ",
    tasting_section_title: "ಕಡ್ಡಾಯ ಆಹಾರ ಗುಣಮಟ್ಟ & ರುಚಿ ಪರೀಕ್ಷೆ",
    tasting_helper: "ಮಕ್ಕಳಿಗೆ ಬಡಿಸುವ 30 ನಿಮಿಷಗಳ ಮೊದಲು ಶಿಕ್ಷಕರು/HM ಪರೀಕ್ಷಿಸಬೇಕು",
    tasting_rating: "ಗುಣಮಟ್ಟ ಮತ್ತು ನೈರ್ಮಲ್ಯ ರೇಟಿಂಗ್",
    tasting_notes: "ರುಚಿ, ತಾಜಾತನ ಮತ್ತು ನೈರ್ಮಲ್ಯ ಅಭಿಪ್ರಾಯ",
    tasting_notes_placeholder: "ಉದಾ: ಅನ್ನ ಸಮರ್ಪಕವಾಗಿ ಬೆಂದಿದೆ, ಸಾಂಬಾರ್ ರುಚಿಕರವಾಗಿದೆ, ನೈರ್ಮಲ್ಯ ಪಾಲಿಸಲಾಗಿದೆ.",
    tasted_by: "ಪರೀಕ್ಷಿಸಿದವರು (ಹೆಸರು ಮತ್ತು ಹುದ್ದೆ)",
    tasted_by_placeholder: "ಉದಾ: ಶೇಖರಯ್ಯ ಎಂ ಎಸ್ (ಮುಖ್ಯೋಪಾಧ್ಯಾಯರು)",
    auto_deduction_preview: "ಸರ್ಕಾರಿ ನಿಯಮಾವಳಿಯಂತೆ ಸ್ವಯಂಚಾಲಿತ ದಾಸ್ತಾನು ಕಡಿತ ಮುನ್ನೋಟ:",
    btn_save_meal: "ಊಟದ ವಿವರ ಉಳಿಸಿ & ದಾಸ್ತಾನು ಕಡಿತಗೊಳಿಸಿ",
    geotag_plate: "ಜಿಯೋಟ್ಯಾಗ್ ಊಟದ ತಟ್ಟೆ ಪರಿಶೀಲನೆ",
    capture_meal_plate: "ಇಂದಿನ ಊಟದ ತಟ್ಟೆಯ ಫೋಟೋ ಸೆರೆಹಿಡಿಯಿರಿ",
    capture_gps_hint: "ಲೈವ್ ಜಿಪಿಎಸ್ ನಿರ್ದೇಶಾಂಕಗಳು ಮತ್ತು ದಿನಾಂಕದೊಂದಿಗೆ ವಾಟರ್‌ಮಾರ್ಕ್ ಆಗುತ್ತದೆ",
    take_plate_photo: "ಜಿಯೋಟ್ಯಾಗ್ ಫೋಟೋ ತೆಗೆಯಿರಿ",
    retake_photo: "ಮರುಚಿತ್ರೀಕರಣ",
    gps_calibrating: "ಜಿಪಿಎಸ್ ಮಾಪನಾಂಕ ನಿರ್ಣಯಿಸಲಾಗುತ್ತಿದೆ...",
    gps_calibrated: "ಜಿಪಿಎಸ್ ಪರಿಶೀಲಿಸಲಾಗಿದೆ",
    gps_locked: "ಜಿಪಿಎಸ್ ಲಾಕ್ ಆಗಿದೆ",
    accuracy_meters: "ನಿಖರತೆ",
    cook_duty_title: "ಅಡುಗೆ ಸಹಾಯಕ ಸಿಬ್ಬಂದಿ ಕರ್ತವ್ಯ ವಿವರ",
    on_duty: "ಹಾಜರಿದ್ದಾರೆ",
    on_leave: "ರಜೆಯಲ್ಲಿದ್ದಾರೆ",
    cook_head_title: "ಮುಖ್ಯ ಅಡುಗೆಯವರು",
    cook_assistant_title: "ಸಹಾಯಕ ಅಡುಗೆಯವರು",
    cook_shift_1: "ಬೆಳಗಿನ ಪಾಳಿ • ಅಡುಗೆ ತಯಾರಿ",
    cook_shift_2: "ಸ್ವಚ್ಛತೆ ಮತ್ತು ಊಟ ಬಡಿಸುವಿಕೆ",
    cook_present_count: "ಹಾಜರಿ",

    // Inventory & Produce
    inv_title: "ದಾಸ್ತಾನು ಮತ್ತು ತಾಜಾ ತರಕಾರಿಗಳ ಲೆಕ್ಕಪುಸ್ತಕ",
    inv_subtitle: "ಅಕ್ಕಿ, ಬೇಳೆ, ಎಣ್ಣೆ ಮತ್ತು ಮಾರುಕಟ್ಟೆಯಿಂದ ಖರೀದಿಸಿದ ತರಕಾರಿಗಳ ಲೆಕ್ಕ",
    tab_inventory_status: "ದಾಸ್ತಾನು ಸ್ಥಿತಿ",
    tab_stock_inward: "ದಾಸ್ತಾನು ಸ್ವೀಕೃತಿ (Inward)",
    tab_fresh_produce: "ತಾಜಾ ತರಕಾರಿಗಳ ಖರೀದಿ",
    tab_transactions: "ವ್ಯವಹಾರಗಳ ವಿವರ (ಲೆಡ್ಜರ್)",
    item_name: "ವಸ್ತುವಿನ ಹೆಸರು",
    category: "ವರ್ಗ",
    current_quantity: "ಲಭ್ಯವಿರುವ ಪ್ರಮಾಣ",
    unit: "ಮಾನದಂಡ",
    threshold: "ಕನಿಷ್ಠ ಮಿತಿ",
    status_col: "ಸ್ಥಿತಿ",
    receipt_date: "ಸ್ವೀಕೃತಿ ದಿನಾಂಕ",
    select_item: "ವಸ್ತು ಆಯ್ಕೆಮಾಡಿ",
    quantity_received: "ಸ್ವೀಕರಿಸಿದ ಪ್ರಮಾಣ",
    vendor_name: "ಸರಬರಾಜುದಾರ / ಅಂಗಡಿಯ ಹೆಸರು",
    bill_number: "ಬಿಲ್ / ಇನ್‌ವಾಯ್ಸ್ ಸಂಖ್ಯೆ",
    total_cost: "ಒಟ್ಟು ವೆಚ್ಚ (ರೂ. ಗಳಲ್ಲಿ)",
    produce_name: "ತರಕಾರಿ / ಹಣ್ಣಿನ ಹೆಸರು",
    produce_name_placeholder: "ಉದಾ: ಟೊಮೆಟೊ, ಆಲೂಗಡ್ಡೆ, ಬೀನ್ಸ್, ಪಾಲಕ್ ಸೊಪ್ಪು",
    produce_name_kn: "ಕನ್ನಡದಲ್ಲಿ ಹೆಸರು",
    produce_kg: "ಪ್ರಮಾಣ (ಕಿಲೋಗ್ರಾಂ)",
    btn_submit_inward: "ದಾಸ್ತಾನು ಸ್ವೀಕೃತಿ ಉಳಿಸಿ",
    btn_submit_produce: "ತರಕಾರಿ ಖರೀದಿ ದಾಖಲಿಸಿ",

    // Reports & Compliance
    rep_title: "ಮಾಸಿಕ ಅಧಿಕೃತ ಅನುಸರಣೆ & ಆಡಿಟ್ ವರದಿ",
    rep_subtitle: "ಕರ್ನಾಟಕ ಶಾಲಾ ಶಿಕ್ಷಣ ಇಲಾಖೆಯ ಅಧಿಕೃತ ನಮೂನೆ",
    select_month: "ವರದಿಯ ತಿಂಗಳು ಆಯ್ಕೆಮಾಡಿ",
    total_working_days: "ಒಟ್ಟು ಕೆಲಸದ ದಿನಗಳು",
    total_meals_month: "ತಿಂಗಳಲ್ಲಿ ಬಡಿಸಿದ ಒಟ್ಟು ಊಟ",
    avg_beneficiaries: "ದೈನಂದಿನ ಸರಾಸರಿ ಫಲಾನುಭವಿಗಳು",
    total_milk_month: "ವಿತರಿಸಿದ ಒಟ್ಟು ಹಾಲು (ಕಪ್)",
    total_eggs_month: "ವಿತರಿಸಿದ ಒಟ್ಟು ಮೊಟ್ಟೆಗಳು",
    consumption_summary: "ಧಾನ್ಯ ಮತ್ತು ಆಹಾರ ಸಾಮಗ್ರಿಗಳ ಬಳಕೆ",
    receipt_summary: "ಸ್ವೀಕರಿಸಿದ ಸಾಮಗ್ರಿಗಳ ಸಾರಾಂಶ",
    item_consumed: "ಬಳಕೆ",
    item_received: "ಸ್ವೀಕರಿಸಿದ್ದು",
    btn_export_pdf: "ವರದಿ ಮುದ್ರಿಸಿ / ಪಿಡಿಎಫ್ ಡೌನ್‌ಲೋಡ್",

    // Audit Trail
    audit_title: "ಸುರಕ್ಷತಾ ಆಡಿಟ್ ಟ್ರಯಲ್ (ದಾಖಲೆಗಳು)",
    audit_subtitle: "ಪ್ರತಿಯೊಂದು ದಾಖಲೆ ಬದಲಾವಣೆ ಮತ್ತು ಬಳಕೆದಾರರ ವಿವರ",
    audit_timestamp: "ದಿನಾಂಕ & ಸಮಯ",
    audit_user: "ಬಳಕೆದಾರ",
    audit_role: "ಹುದ್ದೆ",
    audit_action: "ಕ್ರಿಯೆ",
    audit_details: "ವಿವರಗಳು",
    audit_ip: "ಐಪಿ ವಿಳಾಸ",

    // Cloud & Settings Modal
    settings_title: "ಕ್ಲೌಡ್ ಮತ್ತು ಎಪಿಐ (API) ಸಂಯೋಜನೆ",
    settings_subtitle: "ಫೈರ್‌ಬೇಸ್ (Firebase), ಸ್ಟಿಚ್ (Stitch) ಮತ್ತು ಮೆಟಾ ಕೀಗಳು",
    firebase_status: "ಫೈರ್‌ಬೇಸ್ ಸ್ಥಿತಿ",
    stitch_status: "ಸ್ಟಿಚ್ (Stitch) ಸಂಯೋಜನೆ ಸ್ಥಿತಿ",
    meta_status: "ಮೆಟಾ (Meta) ಆಪ್ ಸ್ಥಿತಿ",
    input_firebase_key: "ಫೈರ್‌ಬೇಸ್ ಎಪಿಐ ಕೀ (API Key)",
    input_firebase_project: "ಫೈರ್‌ಬೇಸ್ ಪ್ರಾಜೆಕ್ಟ್ ಐಡಿ (Project ID)",
    input_stitch_key: "ಸ್ಟಿಚ್ ಎಪಿಐ ಕೀ (Stitch API Key)",
    input_meta_app_id: "ಮೆಟಾ ಆಪ್ ಐಡಿ (Meta App ID)",
    btn_save_keys: "ಕೀಗಳನ್ನು ನವೀಕರಿಸಿ",
    keys_saved_success: "ಎಪಿಐ ಕೀಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ.",

    // Alerts & Notifications
    alert_offline: "ನೀವು ಆಫ್‌ಲೈನ್‌ನಲ್ಲಿದ್ದೀರಿ. ನೆಟ್‌ವರ್ಕ್ ಬಂದಾಗ ಡೇಟಾ ಸಿಂಕ್ ಆಗುತ್ತದೆ.",
    alert_online: "ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕ ಪುನಃಸ್ಥಾಪನೆಯಾಗಿದೆ. ಸರ್ವರ್‌ನೊಂದಿಗೆ ಸಿಂಕ್ ಆಗಿದೆ.",
    alert_success: "ಕಾರ್ಯವು ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!",
    alert_error: "ದೋಷ ಸಂಭವಿಸಿದೆ. ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ ಪುನಃ ಪ್ರಯತ್ನಿಸಿ.",
    offline_badge: "ಆಫ್‌ಲೈನ್ ಮೋಡ್ (2G/3G)",
    online_badge: "ಲೈವ್ ಸರ್ವರ್ ಸಂಪರ್ಕದಲ್ಲಿದೆ"
  }
};

let currentLang = localStorage.getItem("preferred_lang") || "kn"; // Default to Kannada

function setLanguage(lang) {
  if (lang !== "en" && lang !== "kn") lang = "kn";
  currentLang = lang;
  localStorage.setItem("preferred_lang", lang);
  updateDOMTranslations();
}

function toggleLanguage() {
  const nextLang = currentLang === "kn" ? "en" : "kn";
  setLanguage(nextLang);
  return nextLang;
}

function t(key) {
  const dict = translations[currentLang] || translations["en"];
  return dict[key] || translations["en"][key] || key;
}

function updateDOMTranslations() {
  // Update all elements with data-i18n attribute
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (key && translations[currentLang][key]) {
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        if (el.hasAttribute("placeholder")) {
          el.setAttribute("placeholder", translations[currentLang][key]);
        }
      } else {
        el.textContent = translations[currentLang][key];
      }
    }
  });

  // Update elements with data-i18n-placeholder
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (key && translations[currentLang][key]) {
      el.setAttribute("placeholder", translations[currentLang][key]);
    }
  });

  // Update language toggle button text
  const langToggleBtn = document.getElementById("langToggleBtn");
  if (langToggleBtn) {
    langToggleBtn.innerHTML = currentLang === "kn"
      ? '<span class="material-symbols-outlined text-[14px] text-primary">translate</span><span id="current-lang-text">EN</span>'
      : '<span class="material-symbols-outlined text-[14px] text-primary">translate</span><span id="current-lang-text">ಕನ್ನಡ</span>';
  }
  const currentLangEl = document.getElementById("currentLang");
  if (currentLangEl) {
    currentLangEl.textContent = currentLang === "kn" ? "ಕನ್ನಡ" : "EN";
  }

  // Update document title
  document.title = `${t("app_title")} - ${t("school_name_default")}`;
}

// Global exposure
window.i18n = {
  t,
  setLanguage,
  toggleLanguage,
  get currentLang() { return currentLang; },
  updateDOMTranslations
};
