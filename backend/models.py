"""
Pydantic Data Schemas for Mid-Day Meal System (PM-POSHAN)
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
import re

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

# Auth Schemas
class UserLoginPassword(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    password: str

class UserRequestOTP(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)

class UserVerifyOTP(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    otp: Optional[str] = None
    otp_code: Optional[str] = None

class FirebaseAuthPayload(BaseModel):
    id_token: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    photo_url: Optional[str] = None
    role: Optional[str] = "headmaster"

class MetaAuthPayload(BaseModel):
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "headmaster"

class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)

class ResetPasswordRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    otp_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=128)

class UserRegister(BaseModel):
    dise_code: str = Field(..., min_length=4, max_length=20, description="Unified District Information System for Education code")
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=EMAIL_REGEX)
    phone: Optional[str] = Field(None, max_length=15)
    role: str = Field(..., description="headmaster, teacher, or kitchen_staff")
    password: str = Field(..., min_length=6, max_length=128)

class SchoolSetup(BaseModel):
    dise_code: str = Field(..., min_length=4, max_length=20)
    name: str = Field(..., min_length=2, max_length=150)
    name_kn: Optional[str] = Field(None, max_length=150)
    taluk: str = Field("Belur", max_length=100)
    district: str = Field("Hassan", max_length=100)
    state: str = Field("Karnataka", max_length=50)
    head_master_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=EMAIL_REGEX)
    phone: Optional[str] = Field(None, max_length=15)
    password: str = Field(..., min_length=6, max_length=128)

class UserProfile(BaseModel):
    id: int
    school_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    school_name: Optional[str] = None
    dise_code: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

# Attendance Schemas
class AttendanceItem(BaseModel):
    class_id: int
    total_present: int
    boys_present: int
    girls_present: int
    remarks: Optional[str] = None

class AttendanceSubmission(BaseModel):
    date: str
    items: Optional[List[AttendanceItem]] = None
    class_id: Optional[int] = None
    total_present: Optional[int] = None
    boys_present: Optional[int] = None
    girls_present: Optional[int] = None
    remarks: Optional[str] = None

# Meal Log Schemas
class MealRecordCreate(BaseModel):
    date: str
    beneficiaries_served: int
    ksheera_bhagya_milk_count: int = 0
    eggs_distributed: int = 0
    bananas_distributed: int = 0
    chikki_distributed: int = 0
    menu_type: str
    menu_type_kn: str
    tasting_score: int = Field(5, ge=1, le=5)
    tasting_notes: Optional[str] = None
    tasted_by: str
    photo_data: Optional[str] = None  # Base64 data URL or URL
    photo_lat: Optional[float] = None
    photo_lng: Optional[float] = None
    photo_accuracy: Optional[float] = None
    photo_timestamp: Optional[str] = None

class GeotagPhotoUpload(BaseModel):
    photo_data: str  # Data URL or base64
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy_meters: Optional[float] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None

# Inventory Schemas
class StockInwardCreate(BaseModel):
    item_id: int
    quantity: float
    vendor_name: Optional[str] = None
    bill_number: Optional[str] = None
    cost: Optional[float] = 0.0
    date: str
    notes: Optional[str] = None

class StockAdjustmentCreate(BaseModel):
    item_id: int
    new_quantity: float
    reason: str

class FreshProduceCreate(BaseModel):
    item_name: str
    item_name_kn: str
    quantity_kg: float
    cost: float = 0.0
    vendor_name: Optional[str] = None
    bill_no: Optional[str] = None
    date: str
    notes: Optional[str] = None

# Settings & API Keys Schemas
class RuntimeKeysPayload(BaseModel):
    firebase: Optional[dict] = None
    meta: Optional[dict] = None
    stitch: Optional[dict] = None
