"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import logging

from app.config import settings
from app.database import engine, Base
from app.routers import auth, patients, doctors, ai, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("[STARTUP] Starting AI-Powered Radiology Assistant...")
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.upload_directory, exist_ok=True)
    logger.info(f"[STARTUP] Upload directory ready: {settings.upload_directory}")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("[STARTUP] Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("[SHUTDOWN] Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="""
    AI-Powered Radiology Assistant API
    
    ## Features
    - Secure authentication with JWT
    - Role-based access control (Patient, Doctor, Admin)
    - Medical image upload and analysis
    - AI-powered diagnosis assistance
    - Automated report generation
    - AI chatbot for medical queries
    - Medicine suggestions
    
    ## Roles
    - **Patient**: Upload scans, view reports, chat with AI
    - **Doctor**: Review patients, validate reports, prescribe treatments
    - **Admin**: Manage users, monitor system
    
    **Disclaimer**: This is an AI-assisted system. All outputs require professional medical validation.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(ai.router)
app.include_router(admin.router)


@app.get("/")
def root():
    """
    Root endpoint - API welcome message
    """
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to AI-Powered Radiology Assistant API",
        "version": settings.version,
        "documentation": "/docs",
        "status": "operational"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "version": settings.version,
        "app_name": settings.app_name
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
