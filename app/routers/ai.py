"""
AI service routes for chatbot, disease classification, etc.
Specialized for radiology and healthcare topics only.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from app.database import get_db
from app.models import User, ChatSession, ChatMessage, RadiologyScan
from app.schemas import (
    ChatMessageCreate,
    ScanChatRequest,
    ChatMessageResponse,
    DiseaseClassificationRequest,
    MedicineSuggestionResponse
)
from app.utils import get_current_user, TopicValidator
from app.services import gemini_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Services"])


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_ai(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant specialized in radiology and healthcare topics.
    The AI will only respond to medical, radiology, and healthcare-related questions.
    """
    logger.info(f"Chat request from user: {current_user.username} (ID: {current_user.id}), session_id: {message_data.session_id}")
    logger.info(f"User message: {message_data.message[:100]}...")  # Log first 100 chars for monitoring
    
    # Validate message content (basic filtering)
    if not message_data.message or not message_data.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Pre-filter non-medical topics using keyword-based validation
    if not TopicValidator.is_medical_topic(message_data.message):
        logger.info(f"Non-medical topic detected for user {current_user.id}: {message_data.message[:50]}...")
        # We'll still let it through to the AI for more sophisticated filtering
        # but log it for monitoring purposes
    
    # Get or create chat session
    session = None
    
    if message_data.session_id:
        session = db.query(ChatSession)\
            .filter(
                ChatSession.id == message_data.session_id,
                ChatSession.user_id == current_user.id
            )\
            .first()
    
    if not session:
        # Create new session
        session = ChatSession(user_id=current_user.id)
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Created new chat session: {session.id} for user: {current_user.id}")
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        sender="user",
        message=message_data.message
    )
    db.add(user_message)
    db.commit()
    
    # Get conversation history
    history = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session.id)\
        .order_by(ChatMessage.timestamp)\
        .all()
    
    history_data = [
        {"sender": msg.sender, "message": msg.message}
        for msg in history
    ]
    
    try:
        # Get AI response (with built-in topic filtering)
        ai_response_text = await gemini_service.chat_response(
            user_message=message_data.message,
            conversation_history=history_data
        )
        
        logger.info(f"AI response generated for session: {session.id}")
        
    except Exception as e:
        logger.error(f"Error generating AI response for session {session.id}: {str(e)}")
        ai_response_text = "I apologize, but I'm experiencing technical difficulties. Please try again later or contact support for assistance."
    
    # Save AI response
    ai_message = ChatMessage(
        session_id=session.id,
        sender="ai",
        message=ai_response_text
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return ai_message


@router.post("/chat/scan", response_model=ChatMessageResponse)
async def chat_with_ai_about_scan(
    message_data: ScanChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant about a specific radiology scan.
    The AI will have access to the scan's analysis results to provide context-aware responses
    about the particular scan findings, diagnosis, and recommendations.
    """
    logger.info(f"Scan-specific chat request from user: {current_user.username} (ID: {current_user.id}), scan_id: {message_data.scan_id}")
    logger.info(f"User message: {message_data.message[:100]}...")  # Log first 100 chars for monitoring
    
    # Validate message content
    if not message_data.message or not message_data.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Get and validate scan access
    scan = db.query(RadiologyScan).filter(RadiologyScan.id == message_data.scan_id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Check access permissions
    if scan.patient_id != current_user.id and current_user.role.value not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Access denied to this scan")
    
    # Get or create chat session
    session = None
    
    if message_data.session_id:
        session = db.query(ChatSession)\
            .filter(
                ChatSession.id == message_data.session_id,
                ChatSession.user_id == current_user.id
            )\
            .first()
    
    if not session:
        # Create new session
        session = ChatSession(user_id=current_user.id)
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Created new chat session: {session.id} for user: {current_user.id}")
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        sender="user",
        message=message_data.message
    )
    db.add(user_message)
    db.commit()
    
    # Get conversation history
    history = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session.id)\
        .order_by(ChatMessage.timestamp)\
        .all()
    
    history_data = [
        {"sender": msg.sender, "message": msg.message}
        for msg in history
    ]
    
    try:
        # Get AI response with scan context
        ai_response_text = await gemini_service.chat_response_with_scan_context(
            user_message=message_data.message,
            scan=scan,
            conversation_history=history_data
        )
        
        logger.info(f"AI response generated for session: {session.id} with scan context: {message_data.scan_id}")
        
    except Exception as e:
        logger.error(f"Error generating AI response for session {session.id} with scan {message_data.scan_id}: {str(e)}")
        ai_response_text = "I apologize, but I'm experiencing technical difficulties analyzing your scan. Please try again later or contact support for assistance."
    
    # Save AI response
    ai_message = ChatMessage(
        session_id=session.id,
        sender="ai",
        message=ai_response_text
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return ai_message


@router.get("/chat/sessions", response_model=List[dict])
def get_chat_sessions(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all chat sessions for current user.
    """
    sessions = db.query(ChatSession)\
        .filter(ChatSession.user_id == current_user.id)\
        .order_by(desc(ChatSession.session_start))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": s.id,
            "session_start": s.session_start,
            "session_end": s.session_end,
            "message_count": len(s.messages)
        }
        for s in sessions
    ]


@router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages from a specific chat session.
    """
    session = db.query(ChatSession)\
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )\
        .first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session_id)\
        .order_by(ChatMessage.timestamp)\
        .all()
    
    return messages


@router.post("/classify-disease", response_model=dict)
async def classify_disease(
    request: DiseaseClassificationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Classify disease based on symptoms and medical data.
    """
    result = await gemini_service.classify_disease(
        symptoms=request.symptoms,
        medical_history=request.medical_history,
        scan_findings=request.scan_findings
    )
    
    return result


@router.post("/suggest-medicines", response_model=dict)
async def suggest_medicines(
    disease_classification: str,
    symptoms: str,
    patient_age: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-based medicine suggestions.
    
    **Important**: These are informational suggestions only.
    Always consult a healthcare provider before taking any medication.
    """
    result = await gemini_service.suggest_medicines(
        disease_classification=disease_classification,
        symptoms=symptoms,
        patient_age=patient_age
    )
    
    return result


@router.post("/assess-risk", response_model=dict)
async def assess_risk(
    findings: List[str],
    medical_history: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Assess patient risk profile based on findings.
    """
    result = await gemini_service.assess_risk_profile(
        findings=findings,
        medical_history=medical_history
    )
    
    return result
