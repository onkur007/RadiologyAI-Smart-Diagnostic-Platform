"""
File handling utilities for image uploads and validation.
"""
import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from PIL import Image
import aiofiles

from app.config import settings


def validate_file_extension(filename: str) -> bool:
    """
    Validate if file has allowed extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if extension is allowed
    """
    if not filename:
        return False
    
    allowed = settings.get_allowed_extensions()
    extension = filename.split('.')[-1].lower()
    
    return extension in allowed


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to prevent overwrites.
    
    Args:
        original_filename: Original uploaded filename
        
    Returns:
        str: Unique filename with original extension
    """
    extension = original_filename.split('.')[-1].lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{extension}"


async def save_upload_file(upload_file: UploadFile, subfolder: str = "") -> Tuple[str, str]:
    """
    Save an uploaded file to disk.
    
    Args:
        upload_file: FastAPI UploadFile object
        subfolder: Optional subfolder within uploads directory
        
    Returns:
        Tuple[str, str]: (full_path, relative_path)
        
    Raises:
        HTTPException: If file validation fails
    """
    # Validate file extension
    if not validate_file_extension(upload_file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.allowed_extensions}"
        )
    
    # Generate unique filename
    unique_filename = generate_unique_filename(upload_file.filename)
    
    # Create directory structure
    upload_dir = os.path.join(settings.upload_directory, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Full path for saving
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file asynchronously
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await upload_file.read()
            
            # Check file size
            if len(content) > settings.max_upload_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max size: {settings.max_upload_size / 1024 / 1024}MB"
                )
            
            await out_file.write(content)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    
    # Relative path for database storage
    relative_path = os.path.join(subfolder, unique_filename)
    
    return file_path, relative_path


def validate_image_file(file_path: str) -> bool:
    """
    Validate if file is a valid image using PIL.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        bool: True if valid image
    """
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def get_image_info(file_path: str) -> Optional[dict]:
    """
    Get image information (dimensions, format, etc.)
    
    Args:
        file_path: Path to the image file
        
    Returns:
        dict: Image information or None if invalid
    """
    try:
        with Image.open(file_path) as img:
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height
            }
    except Exception:
        return None


def delete_file(file_path: str) -> bool:
    """
    Delete a file from disk.
    
    Args:
        file_path: Path to file
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
