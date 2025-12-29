"""
Admin routes for user management and system monitoring.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging

from app.database import get_db
from app.models import User, RadiologyScan, MedicalReport, UserRole, ReportStatus, SystemLog
from app.schemas import UserResponse, UserRoleUpdate, SystemStats
from app.utils import get_current_user
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role"""
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Non-admin user {current_user.username} attempted to access admin endpoint")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    role: UserRole = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all users in the system.
    Optionally filter by role.
    """
    logger.info(f"Admin {current_user.username} (ID: {current_user.id}) requested user list, role filter: {role}")
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(users)} users for admin {current_user.username}")
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific user.
    """
    logger.info(f"Admin {current_user.username} requested details for user ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        logger.warning(f"User ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"Retrieved details for user: {user.username} (ID: {user_id})")
    return user


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user's role.
    """
    logger.info(f"Admin {current_user.username} updating role for user ID: {user_id} to {role_update.role}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        logger.warning(f"User ID {user_id} not found for role update")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from changing their own role
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot change your own role"
        )
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    
    # Log the action
    log = SystemLog(
        user_id=current_user.id,
        action="ROLE_UPDATE",
        details=f"Changed user {user_id} role to {role_update.role.value}"
    )
    db.add(log)
    db.commit()
    
    return user


@router.put("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate a user account.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    # Log the action
    log = SystemLog(
        user_id=current_user.id,
        action="USER_STATUS_CHANGE",
        details=f"User {user_id} active status: {user.is_active}"
    )
    db.add(log)
    db.commit()
    
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user account (use with caution).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    # Log before deletion
    log = SystemLog(
        user_id=current_user.id,
        action="USER_DELETION",
        details=f"Deleted user {user_id} ({user.username})"
    )
    db.add(log)
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/system-stats", response_model=SystemStats)
def get_system_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive system statistics.
    """
    total_users = db.query(func.count(User.id)).scalar()
    total_patients = db.query(func.count(User.id)).filter(User.role == UserRole.PATIENT).scalar()
    total_doctors = db.query(func.count(User.id)).filter(User.role == UserRole.DOCTOR).scalar()
    total_scans = db.query(func.count(RadiologyScan.id)).scalar()
    total_reports = db.query(func.count(MedicalReport.id)).scalar()
    pending_reports = db.query(func.count(MedicalReport.id))\
        .filter(MedicalReport.status == ReportStatus.PENDING)\
        .scalar()
    
    # AI analyses today
    today = datetime.utcnow().date()
    ai_analyses_today = db.query(func.count(RadiologyScan.id))\
        .filter(
            RadiologyScan.ai_analyzed == True,
            func.date(RadiologyScan.upload_date) == today
        )\
        .scalar()
    
    return SystemStats(
        total_users=total_users or 0,
        total_patients=total_patients or 0,
        total_doctors=total_doctors or 0,
        total_scans=total_scans or 0,
        total_reports=total_reports or 0,
        pending_reports=pending_reports or 0,
        ai_analyses_today=ai_analyses_today or 0
    )


@router.get("/logs", response_model=List[dict])
def get_system_logs(
    skip: int = 0,
    limit: int = 100,
    action: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get system activity logs.
    """
    query = db.query(SystemLog)
    
    if action:
        query = query.filter(SystemLog.action == action)
    
    logs = query.order_by(desc(SystemLog.timestamp))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp
        }
        for log in logs
    ]


@router.get("/reports/pending-validation", response_model=List[dict])
def get_reports_needing_validation(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all reports pending doctor validation.
    """
    reports = db.query(MedicalReport)\
        .filter(MedicalReport.status == ReportStatus.PENDING)\
        .order_by(desc(MedicalReport.generated_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": report.id,
            "patient_id": report.patient_id,
            "scan_id": report.scan_id,
            "generated_at": report.generated_at,
            "days_pending": (datetime.utcnow() - report.generated_at).days
        }
        for report in reports
    ]
