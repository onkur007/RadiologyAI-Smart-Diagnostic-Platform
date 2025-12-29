"""
Doctor-specific routes for reviewing patients, validating reports, etc.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from app.database import get_db
from app.models import User, RadiologyScan, MedicalReport, UserRole, ReportStatus, RiskLevel
from app.schemas import (
    RadiologyScanResponse,
    MedicalReportResponse,
    MedicalReportCreate,
    DoctorValidation
)
from app.utils import get_current_user
from app.services import gemini_service
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/patients", response_model=List[dict])
def get_assigned_patients(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of patients with pending or recent scans.
    Doctors can see all patients in the system.
    """
    logger.info(f"Doctor {current_user.username} (ID: {current_user.id}) requested patient list")
    if current_user.role != UserRole.DOCTOR:
        logger.warning(f"Non-doctor {current_user.username} attempted to access doctor patient list")
        raise HTTPException(status_code=403, detail="Doctors only")
    
    # Get patients who have uploaded scans
    patients = db.query(User)\
        .filter(User.role == UserRole.PATIENT)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    logger.info(f"Retrieved {len(patients)} patients for doctor {current_user.username}")
    patient_list = []
    for patient in patients:
        # Count scans and reports
        scan_count = db.query(RadiologyScan)\
            .filter(RadiologyScan.patient_id == patient.id)\
            .count()
        
        report_count = db.query(MedicalReport)\
            .filter(MedicalReport.patient_id == patient.id)\
            .count()
        
        pending_reports = db.query(MedicalReport)\
            .filter(
                MedicalReport.patient_id == patient.id,
                MedicalReport.status == ReportStatus.PENDING
            )\
            .count()
        
        patient_list.append({
            "id": patient.id,
            "username": patient.username,
            "full_name": patient.full_name,
            "email": patient.email,
            "total_scans": scan_count,
            "total_reports": report_count,
            "pending_reports": pending_reports
        })
    
    return patient_list


@router.get("/patients/{patient_id}/scans", response_model=List[RadiologyScanResponse])
def get_patient_scans(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all scans for a specific patient.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctors only")
    
    scans = db.query(RadiologyScan)\
        .filter(RadiologyScan.patient_id == patient_id)\
        .order_by(desc(RadiologyScan.upload_date))\
        .all()
    
    return scans


@router.get("/patients/{patient_id}/reports", response_model=List[MedicalReportResponse])
def get_patient_reports(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports for a specific patient.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctors only")
    
    reports = db.query(MedicalReport)\
        .filter(MedicalReport.patient_id == patient_id)\
        .order_by(desc(MedicalReport.generated_at))\
        .all()
    
    return reports


@router.post("/generate-report", response_model=MedicalReportResponse)
async def generate_report(
    report_data: MedicalReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI-assisted medical report for a patient.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctors only")
    
    # Get patient
    patient = db.query(User).filter(User.id == report_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get scan if provided
    scan = None
    if report_data.scan_id:
        scan = db.query(RadiologyScan).filter(RadiologyScan.id == report_data.scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
    
    # Prepare data for AI report generation
    patient_info = {
        "name": patient.full_name,
        "id": patient.id,
        "email": patient.email
    }
    
    scan_info = {}
    ai_findings = {}
    
    if scan:
        scan_info = {
            "modality": scan.modality.value,
            "date": str(scan.upload_date),
            "description": scan.description
        }
        
        if scan.ai_analyzed:
            ai_findings = {
                "abnormalities": json.loads(scan.detected_abnormalities) if scan.detected_abnormalities else [],
                "classification": scan.disease_classification,
                "confidence": scan.confidence_score,
                "risk_level": scan.risk_level.value if scan.risk_level else None,
                "explanation": scan.ai_explanation
            }
    
    # Generate report using AI
    report_content = await gemini_service.generate_medical_report(
        patient_info,
        scan_info,
        ai_findings
    )
    
    # Create report in database
    report = MedicalReport(
        patient_id=report_data.patient_id,
        scan_id=report_data.scan_id,
        doctor_id=current_user.id,
        report_type=report_data.report_type,
        ai_generated_content=report_content,
        status=ReportStatus.PENDING
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.put("/reports/{report_id}/validate", response_model=MedicalReportResponse)
def validate_report(
    report_id: int,
    validation: DoctorValidation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate or reject an AI-generated report with doctor's notes.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctors only")
    
    # Get report
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Update report with doctor validation
    report.doctor_id = current_user.id
    report.doctor_notes = validation.doctor_notes
    report.diagnosis = validation.diagnosis
    report.recommended_treatment = validation.recommended_treatment
    report.medicine_suggestions = validation.medicine_suggestions
    report.status = validation.status
    
    from datetime import datetime
    report.validated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(report)
    
    return report


@router.get("/pending-reports", response_model=List[MedicalReportResponse])
def get_pending_reports(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending reports that need doctor validation.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctors only")
    
    reports = db.query(MedicalReport)\
        .filter(MedicalReport.status == ReportStatus.PENDING)\
        .order_by(desc(MedicalReport.generated_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return reports


@router.post("/suggest-medicines/{patient_id}", response_model=dict)
async def suggest_medicines_for_patient(
    patient_id: int,
    scan_id: Optional[int] = None,
    disease_classification: Optional[str] = None,
    symptoms: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-based medicine suggestions for a patient based on their scan image and analysis.
    Provides Bangladesh-specific medicine recommendations.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctors only")
    
    # Verify patient exists
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get the scan to analyze - either specified scan_id or latest scan
    scan = None
    if scan_id:
        scan = db.query(RadiologyScan).filter(
            RadiologyScan.id == scan_id,
            RadiologyScan.patient_id == patient_id
        ).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found for this patient")
    else:
        # Get the latest scan for the patient
        scan = db.query(RadiologyScan)\
            .filter(RadiologyScan.patient_id == patient_id)\
            .order_by(desc(RadiologyScan.upload_date))\
            .first()
    
    if not scan:
        raise HTTPException(
            status_code=404, 
            detail="No scans found for this patient. Please upload a scan first."
        )
    
    # Prepare scan findings for medicine suggestion
    scan_findings = {}
    if scan.ai_analyzed:
        scan_findings = {
            "abnormalities": json.loads(scan.detected_abnormalities) if scan.detected_abnormalities else [],
            "risk_level": scan.risk_level.value if scan.risk_level else "Unknown",
            "confidence": scan.confidence_score,
            "explanation": scan.ai_explanation,
            "modality": scan.modality.value,
            "classification": scan.disease_classification
        }
        
        # Use AI-detected classification if not provided
        if not disease_classification and scan.disease_classification:
            disease_classification = scan.disease_classification
    
    # If no disease classification provided and scan not analyzed, analyze the scan first
    if not disease_classification and not scan.ai_analyzed:
        logger.info(f"Analyzing scan {scan.id} for medicine suggestions")
        try:
            analysis_result = await gemini_service.analyze_radiology_image(
                image_path=scan.image_path,
                modality=scan.modality,
                patient_context=f"Patient: {patient.full_name}, Age: {patient.date_of_birth}"
            )
            
            # Update scan with analysis
            scan.ai_analyzed = True
            scan.detected_abnormalities = json.dumps(analysis_result.get("abnormalities", []))
            scan.disease_classification = analysis_result.get("disease_classification")
            scan.confidence_score = analysis_result.get("confidence_score", 0.0)
            scan.risk_level = analysis_result.get("risk_level", RiskLevel.LOW)
            scan.ai_explanation = analysis_result.get("explanation", "")
            
            db.commit()
            db.refresh(scan)
            
            # Update scan findings and classification
            scan_findings = {
                "abnormalities": analysis_result.get("abnormalities", []),
                "risk_level": analysis_result.get("risk_level", "Unknown"),
                "confidence": analysis_result.get("confidence_score", 0.0),
                "explanation": analysis_result.get("explanation", ""),
                "modality": scan.modality.value,
                "classification": analysis_result.get("disease_classification")
            }
            disease_classification = analysis_result.get("disease_classification")
            
        except Exception as e:
            logger.error(f"Failed to analyze scan for medicine suggestions: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to analyze scan. Please try again or provide manual classification."
            )
    
    # Ensure we have disease classification
    if not disease_classification:
        raise HTTPException(
            status_code=400,
            detail="Disease classification required. Either provide it manually or ensure scan is analyzed."
        )
    
    # Default symptoms if not provided
    if not symptoms:
        symptoms = "Symptoms based on scan findings and detected abnormalities"
    
    # Calculate patient age if date_of_birth is available
    patient_age = None
    if patient.date_of_birth:
        from datetime import datetime
        today = datetime.now()
        patient_age = today.year - patient.date_of_birth.year
    
    # Get AI suggestions with Bangladesh perspective
    suggestions = await gemini_service.suggest_medicines(
        disease_classification=disease_classification,
        symptoms=symptoms,
        patient_age=patient_age,
        scan_findings=scan_findings
    )
    
    # Add scan context to response
    suggestions["scan_context"] = {
        "scan_id": scan.id,
        "modality": scan.modality.value,
        "upload_date": str(scan.upload_date),
        "analyzed": scan.ai_analyzed,
        "classification": disease_classification,
        "risk_level": scan_findings.get("risk_level")
    }
    
    # Add patient context
    suggestions["patient_context"] = {
        "patient_id": patient.id,
        "name": patient.full_name,
        "age": patient_age
    }
    
    logger.info(f"Generated Bangladesh-specific medicine suggestions for patient {patient.id} based on scan {scan.id}")
    return suggestions


@router.get("/patients/{patient_id}/scans-for-medicine", response_model=List[dict])
def get_patient_scans_for_medicine(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available scans for a patient that can be used for medicine suggestions.
    Returns scans with their analysis status and key findings.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctors only")
    
    # Verify patient exists
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    scans = db.query(RadiologyScan)\
        .filter(RadiologyScan.patient_id == patient_id)\
        .order_by(desc(RadiologyScan.upload_date))\
        .all()
    
    scan_list = []
    for scan in scans:
        scan_info = {
            "id": scan.id,
            "modality": scan.modality.value,
            "upload_date": str(scan.upload_date),
            "description": scan.description,
            "ai_analyzed": scan.ai_analyzed,
            "disease_classification": scan.disease_classification,
            "confidence_score": scan.confidence_score,
            "risk_level": scan.risk_level.value if scan.risk_level else None,
            "has_abnormalities": bool(scan.detected_abnormalities) if scan.ai_analyzed else None
        }
        
        if scan.ai_analyzed and scan.detected_abnormalities:
            try:
                abnormalities = json.loads(scan.detected_abnormalities)
                scan_info["abnormalities_summary"] = len(abnormalities)
                scan_info["key_findings"] = abnormalities[:3]  # First 3 findings
            except:
                scan_info["abnormalities_summary"] = 0
                scan_info["key_findings"] = []
        
        scan_list.append(scan_info)
    
    return scan_list
