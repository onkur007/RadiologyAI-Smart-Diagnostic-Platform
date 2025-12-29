"""
Patient-specific routes for uploading images, viewing reports, etc.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging
from datetime import datetime

from app.database import get_db
from app.models import User, RadiologyScan, MedicalReport, ImageModality, UserRole
from app.schemas import (
    RadiologyScanResponse,
    MedicalReportResponse,
    HealthSummaryResponse,
    ChatMessageCreate,
    ChatMessageResponse
)
from app.utils import get_current_user, save_upload_file
from app.services import gemini_service
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/me", response_model=dict)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get current patient's profile information.
    """
    logger.info(f"Profile request by user: {current_user.username} (ID: {current_user.id})")
    if current_user.role != UserRole.PATIENT:
        logger.warning(f"Non-patient {current_user.username} attempted to access patient profile endpoint")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is for patients only"
        )
    
    logger.info(f"Profile retrieved successfully for patient: {current_user.username}")
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "date_of_birth": current_user.date_of_birth,
        "role": current_user.role,
        "created_at": current_user.created_at
    }


@router.post("/upload-image", response_model=RadiologyScanResponse)
async def upload_radiology_image(
    file: UploadFile = File(...),
    modality: ImageModality = Form(...),
    description: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a radiology image (X-ray, CT, MRI).
    
    - **file**: Image file (jpg, jpeg, png)
    - **modality**: Type of scan (xray, ct, mri)
    - **description**: Optional description
    """
    logger.info(f"Image upload initiated by patient: {current_user.username} (ID: {current_user.id}), modality: {modality}")
    if current_user.role != UserRole.PATIENT:
        logger.warning(f"Non-patient {current_user.username} attempted to upload image")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can upload images"
        )
    
    # Save uploaded file
    file_path, relative_path = await save_upload_file(file, subfolder=f"patient_{current_user.id}")
    logger.info(f"Image uploaded successfully to: {relative_path}")
    
    # Create database record
    scan = RadiologyScan(
        patient_id=current_user.id,
        modality=modality,
        image_path=relative_path,
        description=description,
        ai_analyzed=False
    )
    
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    return scan


@router.post("/scans/{scan_id}/analyze", response_model=RadiologyScanResponse)
async def analyze_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request AI analysis of an uploaded scan.
    """
    # Get scan
    scan = db.query(RadiologyScan).filter(RadiologyScan.id == scan_id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Check ownership
    if scan.patient_id != current_user.id and current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Perform AI analysis
    full_path = f"uploads/{scan.image_path}"
    
    try:
        ai_result = await gemini_service.analyze_radiology_image(
            image_path=full_path,
            modality=scan.modality
        )
        
        # Update scan with AI results
        scan.ai_analyzed = True
        scan.detected_abnormalities = json.dumps(ai_result.get("abnormalities", []))
        scan.disease_classification = ai_result.get("disease_classification", "Unknown")
        scan.confidence_score = ai_result.get("confidence_score", 0.0)
        scan.risk_level = ai_result.get("risk_level", "MEDIUM")
        scan.ai_explanation = ai_result.get("explanation", "")
        
        db.commit()
        db.refresh(scan)
        
        return scan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/scans", response_model=List[RadiologyScanResponse])
def get_my_scans(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all scans uploaded by current patient.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Patients only")
    
    scans = db.query(RadiologyScan)\
        .filter(RadiologyScan.patient_id == current_user.id)\
        .order_by(desc(RadiologyScan.upload_date))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return scans


@router.get("/scans/{scan_id}", response_model=RadiologyScanResponse)
def get_scan_details(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific scan.
    """
    scan = db.query(RadiologyScan).filter(RadiologyScan.id == scan_id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Check access
    if scan.patient_id != current_user.id and current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return scan


@router.get("/reports", response_model=List[MedicalReportResponse])
def get_my_reports(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all medical reports for current patient.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Patients only")
    
    reports = db.query(MedicalReport)\
        .filter(MedicalReport.patient_id == current_user.id)\
        .order_by(desc(MedicalReport.generated_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return reports


@router.get("/health-summary", response_model=dict)
async def get_health_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated health summary for patient.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Patients only")
    
    # Get patient data
    scans = db.query(RadiologyScan)\
        .filter(RadiologyScan.patient_id == current_user.id)\
        .order_by(desc(RadiologyScan.upload_date))\
        .limit(5)\
        .all()
    
    reports = db.query(MedicalReport)\
        .filter(MedicalReport.patient_id == current_user.id)\
        .order_by(desc(MedicalReport.generated_at))\
        .limit(5)\
        .all()
    
    # Prepare data for AI
    patient_data = {
        "name": current_user.full_name,
        "age": None,  # Calculate from date_of_birth if available
        "total_scans": len(scans),
        "total_reports": len(reports)
    }
    
    recent_reports_data = [
        {
            "date": str(r.generated_at),
            "diagnosis": r.diagnosis,
            "status": r.status.value
        }
        for r in reports
    ]
    
    # Generate summary
    summary = await gemini_service.generate_health_summary(patient_data, recent_reports_data)
    
    return {
        "patient_id": current_user.id,
        "total_scans": len(scans),
        "total_reports": len(reports),
        "summary": summary
    }


@router.get("/risk-profile", response_model=dict)
async def get_risk_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive risk profiling based on patient's radiology scans.
    Analyzes all scans to provide risk assessment and recommendations.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Patients only")
    
    logger.info(f"Risk profile requested by patient: {current_user.username} (ID: {current_user.id})")
    
    # Get all patient's scans
    scans = db.query(RadiologyScan)\
        .filter(RadiologyScan.patient_id == current_user.id)\
        .order_by(desc(RadiologyScan.upload_date))\
        .all()
    
    if not scans:
        raise HTTPException(
            status_code=404, 
            detail="No radiology scans found. Please upload at least one scan to generate risk profile."
        )
    
    # Separate analyzed and unanalyzed scans
    analyzed_scans = [scan for scan in scans if scan.ai_analyzed]
    unanalyzed_scans = [scan for scan in scans if not scan.ai_analyzed]
    
    # If no scans are analyzed, analyze the most recent ones
    if not analyzed_scans and unanalyzed_scans:
        logger.info(f"No analyzed scans found for patient {current_user.id}, analyzing recent scans...")
        
        # Analyze up to 3 most recent scans
        scans_to_analyze = unanalyzed_scans[:3]
        
        for scan in scans_to_analyze:
            try:
                full_path = f"uploads/{scan.image_path}"
                
                ai_result = await gemini_service.analyze_radiology_image(
                    image_path=full_path,
                    modality=scan.modality,
                    patient_context=f"Patient: {current_user.full_name}"
                )
                
                # Update scan with AI results
                scan.ai_analyzed = True
                scan.detected_abnormalities = json.dumps(ai_result.get("abnormalities", []))
                scan.disease_classification = ai_result.get("disease_classification", "Unknown")
                scan.confidence_score = ai_result.get("confidence_score", 0.0)
                scan.risk_level = ai_result.get("risk_level", "LOW")
                scan.ai_explanation = ai_result.get("explanation", "")
                
                analyzed_scans.append(scan)
                
            except Exception as e:
                logger.error(f"Failed to analyze scan {scan.id}: {str(e)}")
                continue
        
        # Commit all analyses
        if analyzed_scans:
            db.commit()
    
    if not analyzed_scans:
        raise HTTPException(
            status_code=500,
            detail="Unable to analyze scans for risk profiling. Please try again later."
        )
    
    # Prepare data for risk profiling
    patient_info = {
        "name": current_user.full_name,
        "patient_id": current_user.id,
        "age": None,
        "total_scans": len(scans),
        "analyzed_scans": len(analyzed_scans)
    }
    
    # Calculate age if date of birth is available
    if current_user.date_of_birth:
        today = datetime.now()
        patient_info["age"] = today.year - current_user.date_of_birth.year
    
    # Compile scan findings
    scan_findings = []
    risk_levels = []
    confidence_scores = []
    disease_classifications = []
    
    for scan in analyzed_scans:
        finding = {
            "scan_id": scan.id,
            "modality": scan.modality.value,
            "date": str(scan.upload_date),
            "disease_classification": scan.disease_classification,
            "risk_level": scan.risk_level.value if hasattr(scan.risk_level, 'value') else scan.risk_level,
            "confidence_score": scan.confidence_score,
            "abnormalities": json.loads(scan.detected_abnormalities) if scan.detected_abnormalities else [],
            "explanation": scan.ai_explanation
        }
        scan_findings.append(finding)
        
        # Collect risk data for overall assessment
        if scan.risk_level:
            risk_level_value = scan.risk_level.value if hasattr(scan.risk_level, 'value') else scan.risk_level
            risk_levels.append(risk_level_value)
        if scan.confidence_score:
            confidence_scores.append(scan.confidence_score)
        if scan.disease_classification and scan.disease_classification != "Unknown":
            disease_classifications.append(scan.disease_classification)
    
    # Generate AI-based risk profile
    risk_profile = await gemini_service.generate_risk_profile(
        patient_info=patient_info,
        scan_findings=scan_findings
    )
    
    # Calculate overall risk metrics
    overall_risk = "LOW"
    if "HIGH" in risk_levels:
        overall_risk = "HIGH"
    elif "MEDIUM" in risk_levels:
        overall_risk = "MEDIUM"
    
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    # Count abnormalities across all scans
    total_abnormalities = 0
    abnormality_types = set()
    for scan in analyzed_scans:
        if scan.detected_abnormalities:
            abnormalities = json.loads(scan.detected_abnormalities)
            total_abnormalities += len(abnormalities)
            for abnormality in abnormalities:
                if isinstance(abnormality, dict) and 'type' in abnormality:
                    abnormality_types.add(abnormality['type'])
    
    # Compile comprehensive response
    response = {
        "patient_info": patient_info,
        "risk_summary": {
            "overall_risk_level": overall_risk,
            "confidence_score": round(avg_confidence, 2),
            "total_scans_analyzed": len(analyzed_scans),
            "total_abnormalities_detected": total_abnormalities,
            "unique_abnormality_types": len(abnormality_types),
            "disease_classifications": list(set(disease_classifications))
        },
        "scan_breakdown": scan_findings,
        "ai_risk_assessment": risk_profile,
        "recommendations": {
            "follow_up_required": overall_risk in ["MEDIUM", "HIGH"],
            "urgent_consultation": overall_risk == "HIGH",
            "routine_monitoring": overall_risk == "LOW",
            "next_scan_timeline": "3-6 months" if overall_risk == "HIGH" else "6-12 months"
        },
        "unanalyzed_scans": len(unanalyzed_scans),
        "generated_at": str(datetime.now())
    }
    
    logger.info(f"Risk profile generated for patient {current_user.id}: Overall risk = {overall_risk}")
    return response


@router.get("/latest-scan-risk", response_model=dict)
async def get_latest_scan_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick risk assessment based on patient's latest radiology scan.
    Simpler version of risk profiling for immediate insights.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Patients only")
    
    logger.info(f"Latest scan risk check requested by patient: {current_user.username} (ID: {current_user.id})")
    
    # Get the latest scan
    latest_scan = db.query(RadiologyScan)\
        .filter(RadiologyScan.patient_id == current_user.id)\
        .order_by(desc(RadiologyScan.upload_date))\
        .first()
    
    if not latest_scan:
        raise HTTPException(
            status_code=404,
            detail="No radiology scans found. Please upload a scan first."
        )
    
    # If scan is not analyzed, analyze it
    if not latest_scan.ai_analyzed:
        try:
            full_path = f"uploads/{latest_scan.image_path}"
            
            ai_result = await gemini_service.analyze_radiology_image(
                image_path=full_path,
                modality=latest_scan.modality,
                patient_context=f"Patient: {current_user.full_name}"
            )
            
            # Update scan with AI results
            latest_scan.ai_analyzed = True
            latest_scan.detected_abnormalities = json.dumps(ai_result.get("abnormalities", []))
            latest_scan.disease_classification = ai_result.get("disease_classification", "Unknown")
            latest_scan.confidence_score = ai_result.get("confidence_score", 0.0)
            latest_scan.risk_level = ai_result.get("risk_level", "LOW")
            latest_scan.ai_explanation = ai_result.get("explanation", "")
            
            db.commit()
            db.refresh(latest_scan)
            
        except Exception as e:
            logger.error(f"Failed to analyze latest scan for patient {current_user.id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Unable to analyze scan. Please try again later."
            )
    
    # Prepare risk information
    abnormalities = []
    if latest_scan.detected_abnormalities:
        try:
            abnormalities = json.loads(latest_scan.detected_abnormalities)
        except:
            abnormalities = []
    
    risk_level = latest_scan.risk_level.value if hasattr(latest_scan.risk_level, 'value') else latest_scan.risk_level
    
    # Generate simple risk interpretation
    risk_interpretation = {
        "LOW": {
            "description": "Low risk detected",
            "meaning": "No significant abnormalities found. Routine monitoring recommended.",
            "action": "Continue regular health check-ups",
            "urgency": "Routine"
        },
        "MEDIUM": {
            "description": "Moderate risk detected",
            "meaning": "Some abnormalities found that require attention and monitoring.",
            "action": "Schedule follow-up with healthcare provider within 2-4 weeks",
            "urgency": "Moderate"
        },
        "HIGH": {
            "description": "High risk detected",
            "meaning": "Significant findings that require immediate medical attention.",
            "action": "Consult with doctor immediately, urgent evaluation needed",
            "urgency": "High"
        }
    }
    
    interpretation = risk_interpretation.get(risk_level, risk_interpretation["LOW"])
    
    response = {
        "scan_info": {
            "scan_id": latest_scan.id,
            "modality": latest_scan.modality.value,
            "upload_date": str(latest_scan.upload_date),
            "description": latest_scan.description
        },
        "risk_assessment": {
            "risk_level": risk_level,
            "confidence_score": latest_scan.confidence_score,
            "disease_classification": latest_scan.disease_classification,
            "interpretation": interpretation
        },
        "findings": {
            "total_abnormalities": len(abnormalities),
            "abnormalities": abnormalities,
            "ai_explanation": latest_scan.ai_explanation
        },
        "recommendations": {
            "immediate_action": interpretation["action"],
            "follow_up_timeline": "1-2 weeks" if risk_level == "HIGH" else "1-3 months",
            "lifestyle_tips": [
                "Maintain a healthy diet with plenty of fruits and vegetables",
                "Stay hydrated, especially in Bangladesh's climate",
                "Regular exercise as appropriate for your condition",
                "Avoid smoking and limit alcohol consumption",
                "Follow up with healthcare providers as recommended"
            ]
        },
        "next_steps": {
            "complete_risk_profile": "Get comprehensive risk profile at /patients/risk-profile",
            "consult_doctor": "Book appointment for detailed consultation",
            "monitor_symptoms": "Watch for any new or worsening symptoms"
        },
        "generated_at": str(datetime.now())
    }
    
    logger.info(f"Latest scan risk assessment completed for patient {current_user.id}: Risk level = {risk_level}")
    return response
