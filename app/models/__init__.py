"""
SQLAlchemy database models for the Radiology AI application.
Defines database tables and relationships.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ImageModality(str, enum.Enum):
    """Medical image modality types"""
    XRAY = "xray"
    CT = "ct"
    MRI = "mri"


class ReportStatus(str, enum.Enum):
    """Report validation status"""
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


class User(Base):
    """User model for authentication and role management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)
    phone = Column(String(20))
    date_of_birth = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships - using both primaryjoin and foreign_keys for multi-FK tables
    radiology_images = relationship(
        "RadiologyScan", 
        back_populates="patient", 
        primaryjoin="User.id == foreign(RadiologyScan.patient_id)"
    )
    reports = relationship(
        "MedicalReport", 
        back_populates="patient", 
        primaryjoin="User.id == foreign(MedicalReport.patient_id)"
    )
    assigned_scans = relationship(
        "RadiologyScan", 
        back_populates="doctor", 
        primaryjoin="User.id == foreign(RadiologyScan.doctor_id)"
    )
    validated_reports = relationship(
        "MedicalReport", 
        back_populates="doctor", 
        primaryjoin="User.id == foreign(MedicalReport.doctor_id)"
    )
    chat_sessions = relationship("ChatSession", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class RadiologyScan(Base):
    """Radiology scan/image uploads"""
    __tablename__ = "radiology_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    modality = Column(SQLEnum(ImageModality), nullable=False)
    image_path = Column(String(500), nullable=False)
    upload_date = Column(DateTime, server_default=func.now())
    description = Column(Text)
    
    # AI Analysis Results
    ai_analyzed = Column(Boolean, default=False)
    detected_abnormalities = Column(Text)  # JSON string
    disease_classification = Column(String(255))
    confidence_score = Column(Float)
    risk_level = Column(SQLEnum(RiskLevel))
    ai_explanation = Column(Text)
    
    # Relationships
    patient = relationship("User", back_populates="radiology_images", foreign_keys=[patient_id])
    doctor = relationship("User", back_populates="assigned_scans", foreign_keys=[doctor_id])
    report = relationship("MedicalReport", back_populates="scan", uselist=False)
    
    def __repr__(self):
        return f"<RadiologyScan {self.id} - {self.modality}>"


class MedicalReport(Base):
    """Generated medical reports"""
    __tablename__ = "medical_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scan_id = Column(Integer, ForeignKey("radiology_scans.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Report Content
    report_type = Column(String(100))
    ai_generated_content = Column(Text)
    doctor_notes = Column(Text)
    diagnosis = Column(Text)
    recommended_treatment = Column(Text)
    medicine_suggestions = Column(Text)  # JSON string
    
    # Status
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    generated_at = Column(DateTime, server_default=func.now())
    validated_at = Column(DateTime)
    
    # Relationships
    patient = relationship("User", back_populates="reports", foreign_keys=[patient_id])
    scan = relationship("RadiologyScan", back_populates="report")
    doctor = relationship("User", back_populates="validated_reports", foreign_keys=[doctor_id])
    
    def __repr__(self):
        return f"<MedicalReport {self.id} - {self.status}>"


class ChatSession(Base):
    """AI chatbot conversation sessions"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_start = Column(DateTime, server_default=func.now())
    session_end = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession {self.id} - User {self.user_id}>"


class ChatMessage(Base):
    """Individual chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # 'user' or 'ai'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage {self.id} - {self.sender}>"


class SystemLog(Base):
    """System activity and audit logs"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<SystemLog {self.id} - {self.action}>"
