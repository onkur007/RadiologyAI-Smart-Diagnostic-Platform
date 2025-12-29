# Project Structure

```
RadiologyAI/
│
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database connection and session
│   │
│   ├── models/                  # Database models (SQLAlchemy)
│   │   └── __init__.py         # User, Scan, Report, Chat models
│   │
│   ├── schemas/                 # Pydantic schemas (validation)
│   │   └── __init__.py         # Request/response schemas
│   │
│   ├── routers/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── patients.py         # Patient-specific endpoints
│   │   ├── doctors.py          # Doctor-specific endpoints
│   │   ├── ai.py               # AI service endpoints
│   │   └── admin.py            # Admin endpoints
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   └── ai_service.py       # Gemini AI integration
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── security.py         # Authentication & authorization
│       └── file_handler.py     # File upload handling
│
├── uploads/                     # Uploaded images storage
│   └── .gitkeep
│
├── tests/                       # Unit tests
│   ├── __init__.py
│   └── test_api.py             # API tests
│
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── init_db.py                   # Database initialization script
│
├── README.md                    # Project overview
├── INSTALLATION.md              # Detailed installation guide
├── API_GUIDE.md                 # API usage documentation
├── QUICKSTART.md                # Quick start guide
└── PROJECT_STRUCTURE.md         # This file

```

## File Descriptions

### Core Application Files

- **app/main.py**: FastAPI application setup, middleware, and route inclusion
- **app/config.py**: Environment variables and application settings
- **app/database.py**: SQLAlchemy engine, session factory, and database connection

### Models (app/models/)

Database table definitions:
- **User**: User accounts with roles (patient, doctor, admin)
- **RadiologyScan**: Uploaded medical images and AI analysis
- **MedicalReport**: Generated reports with doctor validation
- **ChatSession/ChatMessage**: AI chatbot conversations
- **SystemLog**: Audit logs for system activities

### Schemas (app/schemas/)

Pydantic models for data validation:
- Request schemas: UserCreate, RadiologyScanCreate, etc.
- Response schemas: UserResponse, RadiologyScanResponse, etc.
- Validation and serialization

### Routers (app/routers/)

API endpoint definitions:
- **auth.py**: Registration, login, token management
- **patients.py**: Patient image upload, viewing scans/reports
- **doctors.py**: Patient management, report validation
- **ai.py**: AI chat, disease classification, medicine suggestions
- **admin.py**: User management, system statistics

### Services (app/services/)

Business logic and external integrations:
- **ai_service.py**: 
  - Image analysis with Gemini Vision
  - Disease classification
  - Report generation
  - Chatbot responses
  - Medicine suggestions

### Utils (app/utils/)

Helper functions:
- **security.py**: Password hashing, JWT tokens, role checking
- **file_handler.py**: File upload, validation, storage

### Configuration Files

- **.env**: Private configuration (not committed to git)
- **.env.example**: Template for environment variables
- **requirements.txt**: Python package dependencies
- **.gitignore**: Files to exclude from version control

### Scripts

- **init_db.py**: Initialize database, create tables, seed admin user

### Documentation

- **README.md**: Project overview and quick start
- **INSTALLATION.md**: Detailed setup instructions
- **API_GUIDE.md**: Complete API reference
- **QUICKSTART.md**: 5-minute setup guide
- **PROJECT_STRUCTURE.md**: This file

### Tests

- **tests/test_api.py**: Unit tests for API endpoints
- Run with: `pytest tests/`

## Data Flow

1. **User Registration/Login** → JWT Token
2. **Patient Uploads Image** → Stored in `uploads/`
3. **AI Analysis Requested** → Gemini API processes image
4. **Results Stored** → Database (RadiologyScan)
5. **Doctor Reviews** → Validates or rejects
6. **Report Generated** → Stored in MedicalReport
7. **Patient Views** → Accesses through API

## Technology Stack

- **Web Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **AI Engine**: Google Gemini API
- **File Storage**: Local filesystem (uploads/)
- **Validation**: Pydantic
- **Testing**: pytest

## Security Layers

1. **Authentication**: JWT token-based
2. **Authorization**: Role-based access control (RBAC)
3. **Password**: Bcrypt hashing
4. **File Upload**: Extension and size validation
5. **API**: CORS middleware configured

## Database Schema

```
users
├── id (PK)
├── username (unique)
├── email (unique)
├── hashed_password
├── role (patient/doctor/admin)
└── ... (profile fields)

radiology_scans
├── id (PK)
├── patient_id (FK → users)
├── doctor_id (FK → users)
├── image_path
├── modality (xray/ct/mri)
├── ai_analyzed
└── ... (AI analysis fields)

medical_reports
├── id (PK)
├── patient_id (FK → users)
├── scan_id (FK → radiology_scans)
├── doctor_id (FK → users)
├── ai_generated_content
├── doctor_notes
├── status (pending/validated/rejected)
└── ... (report fields)

chat_sessions
├── id (PK)
├── user_id (FK → users)
└── ... (session fields)

chat_messages
├── id (PK)
├── session_id (FK → chat_sessions)
├── sender (user/ai)
└── message

system_logs
├── id (PK)
├── user_id (FK → users)
├── action
└── ... (log fields)
```

## API Organization

```
/                           # Root endpoint
/health                     # Health check
/docs                       # Swagger UI
/redoc                      # ReDoc UI

/auth
├── /register              # User registration
├── /login                 # User login
└── /login-json            # JSON login

/patients
├── /me                    # Get profile
├── /upload-image          # Upload scan
├── /scans                 # List scans
├── /scans/{id}           # Scan details
├── /scans/{id}/analyze   # Analyze scan
├── /reports              # List reports
└── /health-summary       # Health summary

/doctors
├── /patients             # List patients
├── /patients/{id}/scans  # Patient scans
├── /patients/{id}/reports # Patient reports
├── /generate-report      # Generate report
├── /reports/{id}/validate # Validate report
├── /pending-reports      # Pending reports
└── /suggest-medicines/{id} # Medicine suggestions

/ai
├── /chat                 # Chat with AI
├── /chat/sessions        # Chat sessions
├── /chat/sessions/{id}/messages # Session messages
├── /classify-disease     # Disease classification
├── /suggest-medicines    # Medicine suggestions
└── /assess-risk          # Risk assessment

/admin
├── /users                # List users
├── /users/{id}          # User details
├── /users/{id}/role     # Update role
├── /users/{id}/toggle-active # Toggle active
├── /users/{id}          # Delete user
├── /system-stats        # System statistics
├── /logs                # System logs
└── /reports/pending-validation # Pending reports
```

## Extension Points

To add new features:

1. **New Model**: Add to `app/models/__init__.py`
2. **New Schema**: Add to `app/schemas/__init__.py`
3. **New Endpoint**: Create router in `app/routers/`
4. **New AI Feature**: Extend `app/services/ai_service.py`
5. **New Utility**: Add to `app/utils/`

## Best Practices

- Keep routers focused on single responsibility
- Business logic goes in services, not routers
- Use Pydantic schemas for all inputs/outputs
- Always validate file uploads
- Log important actions to system_logs
- Include medical disclaimers in AI outputs
- Test new features with pytest
