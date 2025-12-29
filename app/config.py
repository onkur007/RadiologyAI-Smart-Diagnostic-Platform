"""
Configuration settings for the Radiology AI application.
Loads environment variables and provides application-wide settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Info
    app_name: str = "AI-Powered Radiology Assistant"
    version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://postgres:rahul2195@localhost:5432/radiology_ai"
    
    # Security
    secret_key: str = "$+xdrts12rr1$qf4)r$i9o4acpe(ag7j%df+vilh(0yekvlug"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Configuration
    gemini_api_key: str = "AIzaSyCurgdTCjBq7n533fkxTpVtEkKKVgFah3w"
    
    # File Upload
    max_upload_size: int = 10485760  # 10MB
    allowed_extensions: str = "jpg,jpeg,png"
    upload_directory: str = "uploads"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_allowed_origins(self) -> List[str]:
        """Parse allowed origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def get_allowed_extensions(self) -> List[str]:
        """Parse allowed file extensions from comma-separated string"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]


# Create global settings instance
settings = Settings()
