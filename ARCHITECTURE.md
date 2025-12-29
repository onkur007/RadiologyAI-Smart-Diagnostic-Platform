# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Browser │  │ Postman  │  │  Mobile  │  │  Python  │   │
│  │   /docs  │  │  Client  │  │   App    │  │  Client  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │ HTTP/HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │                CORS Middleware                      │     │
│  │                Authentication                       │     │
│  │                Rate Limiting (future)               │     │
│  └────────────────────────────────────────────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Router 1   │    │   Router 2   │    │   Router 3   │
│     Auth     │    │   Patients   │    │   Doctors    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       ▼                   ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Security   │  │  AI Service  │  │ File Handler │      │
│  │   Service    │  │   (Gemini)   │  │   Service    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌─────────┐      ┌─────────────┐      ┌─────────┐
    │   JWT   │      │   Gemini    │      │  Local  │
    │  Tokens │      │     API     │      │ Storage │
    └─────────┘      └─────────────┘      └─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ SQLAlchemy   │  │  PostgreSQL  │  │   Models     │      │
│  │     ORM      │◄─┤   Database   │──┤   (Tables)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Flow

### 1. Authentication Flow
```
User Login Request
      │
      ▼
[POST /auth/login]
      │
      ▼
Check Username/Password
      │
      ├─ Invalid ──► 401 Unauthorized
      │
      ├─ Valid ────► Generate JWT Token
      │                    │
      │                    ▼
      │            Return Token + User Info
      │                    │
      ▼                    ▼
Store Token          Use Token in Headers
                     (Authorization: Bearer <token>)
```

### 2. Image Upload & Analysis Flow
```
Patient Uploads Image
         │
         ▼
[POST /patients/upload-image]
         │
         ├─ Validate Token
         ├─ Check File Type
         ├─ Check File Size
         │
         ▼
Save to Disk (uploads/)
         │
         ▼
Create DB Record (radiology_scans)
         │
         ▼
[POST /patients/scans/{id}/analyze]
         │
         ▼
Load Image from Disk
         │
         ▼
Send to Gemini Vision API
         │
         ▼
Receive AI Analysis
         │
         ├─ Abnormalities
         ├─ Disease Classification
         ├─ Confidence Score
         ├─ Risk Level
         │
         ▼
Update DB Record with Results
         │
         ▼
Return Analysis to Patient
```

### 3. Report Generation Flow
```
Doctor Selects Patient
         │
         ▼
[POST /doctors/generate-report]
         │
         ├─ Get Patient Info
         ├─ Get Scan Details
         ├─ Get AI Findings
         │
         ▼
Build Report Context
         │
         ▼
Send to Gemini Text API
         │
         ▼
Receive Generated Report
         │
         ▼
Create DB Record (medical_reports)
         │
         ▼
Return Report to Doctor
         │
         ▼
[PUT /doctors/reports/{id}/validate]
         │
         ├─ Add Doctor Notes
         ├─ Add Diagnosis
         ├─ Add Treatment Plan
         │
         ▼
Update Report Status (validated)
         │
         ▼
Notify Patient (future feature)
```

### 4. Chatbot Interaction Flow
```
User Sends Message
         │
         ▼
[POST /ai/chat]
         │
         ├─ Get/Create Session
         ├─ Load Chat History
         │
         ▼
Build Conversation Context
         │
         ▼
Send to Gemini Text API
         │
         ▼
Receive AI Response
         │
         ▼
Save User Message to DB
         │
         ▼
Save AI Response to DB
         │
         ▼
Return Response to User
```

---

## Database Schema

```
┌─────────────────────┐
│       users         │
├─────────────────────┤
│ id (PK)            │
│ username (unique)  │
│ email (unique)     │
│ hashed_password    │
│ role (enum)        │◄────────┐
│ full_name          │         │
│ phone              │         │
│ is_active          │         │
└─────────┬───────────┘         │
          │                     │
          │ 1:N                 │ 1:N
          ▼                     │
┌─────────────────────┐         │
│  radiology_scans    │         │
├─────────────────────┤         │
│ id (PK)            │         │
│ patient_id (FK)    │─────────┘
│ doctor_id (FK)     │
│ modality (enum)    │
│ image_path         │
│ ai_analyzed        │
│ detected_abn...    │
│ disease_class...   │
│ confidence_score   │
│ risk_level         │
└─────────┬───────────┘
          │ 1:1
          ▼
┌─────────────────────┐         ┌─────────────────────┐
│  medical_reports    │         │   chat_sessions     │
├─────────────────────┤         ├─────────────────────┤
│ id (PK)            │         │ id (PK)            │
│ patient_id (FK)    │─────────┤ user_id (FK)       │
│ scan_id (FK)       │         │ session_start      │
│ doctor_id (FK)     │         │ session_end        │
│ ai_generated...    │         └─────────┬───────────┘
│ doctor_notes       │                   │ 1:N
│ diagnosis          │                   ▼
│ status (enum)      │         ┌─────────────────────┐
└────────────────────┘         │   chat_messages     │
                               ├─────────────────────┤
┌─────────────────────┐        │ id (PK)            │
│    system_logs      │        │ session_id (FK)    │
├─────────────────────┤        │ sender             │
│ id (PK)            │        │ message            │
│ user_id (FK)       │        │ timestamp          │
│ action             │        └────────────────────┘
│ details            │
│ timestamp          │
└────────────────────┘
```

---

## Component Responsibilities

### API Layer (FastAPI)
- ✅ Handle HTTP requests
- ✅ Route to appropriate handlers
- ✅ Validate input data
- ✅ Authenticate users
- ✅ Authorize access
- ✅ Return responses

### Router Layer
- ✅ Define endpoints
- ✅ Parse request data
- ✅ Call service functions
- ✅ Format responses
- ✅ Handle errors

### Service Layer
- ✅ Business logic
- ✅ AI integration
- ✅ File operations
- ✅ External API calls
- ✅ Data processing

### Data Layer
- ✅ Database operations
- ✅ CRUD functions
- ✅ Relationships
- ✅ Queries
- ✅ Transactions

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
│                                                              │
│  Layer 1: Authentication                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  JWT Token Validation                              │    │
│  │  Password Hashing (bcrypt)                         │    │
│  │  Token Expiration (30 min)                         │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 2: Authorization                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Role-Based Access Control                         │    │
│  │  Endpoint Permissions                              │    │
│  │  Resource Ownership                                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 3: Input Validation                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Pydantic Schemas                                  │    │
│  │  File Type Validation                              │    │
│  │  Size Limits                                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 4: Data Protection                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  SQL Injection Prevention (ORM)                    │    │
│  │  XSS Protection                                    │    │
│  │  CORS Configuration                                │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Development
```
┌───────────────────┐
│   Local Machine   │
│                   │
│  ┌─────────────┐ │
│  │   Python    │ │
│  │   FastAPI   │ │
│  │  (port 8000)│ │
│  └─────────────┘ │
│                   │
│  ┌─────────────┐ │
│  │ PostgreSQL  │ │
│  │ (port 5432) │ │
│  └─────────────┘ │
└───────────────────┘
```

### Docker
```
┌─────────────────────────────────────────┐
│         Docker Compose                   │
│                                          │
│  ┌────────────────┐  ┌────────────────┐│
│  │  app container │  │  db container  ││
│  │                │  │                ││
│  │    FastAPI     │──│   PostgreSQL   ││
│  │   (port 8000)  │  │   (port 5432)  ││
│  └────────────────┘  └────────────────┘│
│                                          │
│  ┌────────────────┐                     │
│  │   volumes      │                     │
│  │   - uploads    │                     │
│  │   - postgres   │                     │
│  └────────────────┘                     │
└─────────────────────────────────────────┘
```

### Production (Example)
```
┌─────────────────────────────────────────────────────────────┐
│                      Cloud Platform                          │
│                                                              │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐   │
│  │ Load       │      │   API      │      │  Database  │   │
│  │ Balancer   │─────▶│  Server    │─────▶│  (RDS)     │   │
│  │            │      │  (EC2/ECS) │      │            │   │
│  └────────────┘      └────────────┘      └────────────┘   │
│                                                              │
│  ┌────────────┐      ┌────────────┐                        │
│  │   Object   │      │   Cache    │                        │
│  │  Storage   │      │  (Redis)   │                        │
│  │   (S3)     │      │  [future]  │                        │
│  └────────────┘      └────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Technology Stack                         │
│                                                              │
│  Frontend (Future)                                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  React / Vue / Flutter                             │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼ HTTP/HTTPS                        │
│  Backend                                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  FastAPI (Python 3.9+)                             │    │
│  │  - Uvicorn ASGI Server                             │    │
│  │  - Pydantic Validation                             │    │
│  │  - JWT Authentication                              │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  AI / External APIs                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Google Gemini API                                 │    │
│  │  - Gemini Pro (text)                               │    │
│  │  - Gemini Pro Vision (images)                      │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  Database                                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PostgreSQL 12+                                    │    │
│  │  - SQLAlchemy ORM                                  │    │
│  │  - Alembic Migrations                              │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  Storage                                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Local Filesystem / S3 (future)                    │    │
│  │  - Medical Images                                  │    │
│  │  - Reports                                         │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

This architecture provides:
- ✅ Scalability
- ✅ Maintainability
- ✅ Security
- ✅ Modularity
- ✅ Testability
- ✅ Clear separation of concerns
