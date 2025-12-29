"""
Pydantic schemas for request/response validation.
These schemas define the structure of API inputs and outputs.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, RiskLevel, ImageModality, ReportStatus


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.PATIENT


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response (without sensitive data)"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== Radiology Scan Schemas ====================

class RadiologyScanCreate(BaseModel):
    """Schema for uploading radiology scan"""
    modality: ImageModality
    description: Optional[str] = None


class AIAnalysisResult(BaseModel):
    """AI analysis results"""
    detected_abnormalities: Optional[str] = None
    disease_classification: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    risk_level: Optional[RiskLevel] = None
    ai_explanation: Optional[str] = None


class RadiologyScanResponse(BaseModel):
    """Schema for radiology scan response"""
    id: int
    patient_id: int
    doctor_id: Optional[int] = None
    modality: ImageModality
    image_path: str
    upload_date: datetime
    description: Optional[str] = None
    ai_analyzed: bool
    detected_abnormalities: Optional[str] = None
    disease_classification: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_level: Optional[RiskLevel] = None
    ai_explanation: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== Medical Report Schemas ====================

class MedicalReportCreate(BaseModel):
    """Schema for creating medical report"""
    patient_id: int
    scan_id: Optional[int] = None
    report_type: str = "AI Generated"


class DoctorValidation(BaseModel):
    """Schema for doctor validation of report"""
    doctor_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    recommended_treatment: Optional[str] = None
    medicine_suggestions: Optional[str] = None
    status: ReportStatus


class MedicalReportResponse(BaseModel):
    """Schema for medical report response"""
    id: int
    patient_id: int
    scan_id: Optional[int] = None
    doctor_id: Optional[int] = None
    report_type: str
    ai_generated_content: Optional[str] = None
    doctor_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    recommended_treatment: Optional[str] = None
    medicine_suggestions: Optional[str] = None
    status: ReportStatus
    generated_at: datetime
    validated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== Chat Schemas ====================

class ChatMessageCreate(BaseModel):
    """Schema for creating chat message"""
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[int] = None


class ScanChatRequest(BaseModel):
    """Schema for scan-specific chat request"""
    message: str = Field(..., min_length=1, max_length=5000)
    scan_id: int = Field(..., description="ID of the radiology scan to discuss")
    session_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    session_id: int
    sender: str
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """Schema for chat session response"""
    id: int
    user_id: int
    session_start: datetime
    session_end: Optional[datetime] = None
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True


# ==================== AI Service Schemas ====================

class ImageAnalysisRequest(BaseModel):
    """Request schema for image analysis"""
    scan_id: int


class DiseaseClassificationRequest(BaseModel):
    """Request schema for disease classification"""
    symptoms: str
    medical_history: Optional[str] = None
    scan_findings: Optional[str] = None


class HealthSummaryResponse(BaseModel):
    """Patient health summary"""
    patient_id: int
    total_scans: int
    total_reports: int
    risk_profile: Optional[RiskLevel] = None
    recent_findings: List[str] = []
    recommended_actions: List[str] = []


class MedicineSuggestion(BaseModel):
    """Medicine suggestion schema"""
    medicine_name: str
    purpose: str
    general_usage: str
    precautions: Optional[str] = None


class MedicineSuggestionResponse(BaseModel):
    """Response with medicine suggestions"""
    disease_category: str
    suggestions: List[MedicineSuggestion]
    disclaimer: str = "These are AI-generated suggestions only. Consult a doctor before taking any medication."


# ==================== Admin Schemas ====================

class SystemStats(BaseModel):
    """System statistics for admin"""
    total_users: int
    total_patients: int
    total_doctors: int
    total_scans: int
    total_reports: int
    pending_reports: int
    ai_analyses_today: int


class UserRoleUpdate(BaseModel):
    """Schema for updating user role"""
    role: UserRole


# ==================== Error Response Schema ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    code: Optional[str] = None
