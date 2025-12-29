"""
Utility functions and helpers.
"""
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user,
    get_current_active_user,
    RoleChecker,
    require_patient,
    require_doctor,
    require_admin,
    require_doctor_or_admin,
    require_patient_or_doctor
)

from app.utils.file_handler import (
    validate_file_extension,
    generate_unique_filename,
    save_upload_file,
    validate_image_file,
    get_image_info,
    delete_file
)

from app.utils.topic_validator import TopicValidator

__all__ = [
    # Security
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'authenticate_user',
    'get_current_user',
    'get_current_active_user',
    'RoleChecker',
    'require_patient',
    'require_doctor',
    'require_admin',
    'require_doctor_or_admin',
    'require_patient_or_doctor',
    
    # File handling
    'validate_file_extension',
    'generate_unique_filename',
    'save_upload_file',
    'validate_image_file',
    'get_image_info',
    'delete_file',
    
    # Topic validation
    'TopicValidator',
]
