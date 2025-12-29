# API Usage Guide

Complete guide to using the AI-Powered Radiology Assistant API.

---

## 🔐 Authentication

All protected endpoints require JWT authentication.

### Register a New User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Full Name",
  "password": "secure_password",
  "role": "patient",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01T00:00:00"
}
```

**Roles**: `patient`, `doctor`, `admin`

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "username",
    "email": "user@example.com",
    "role": "patient",
    ...
  }
}
```

### Using the Token

Include the token in the Authorization header for all subsequent requests:

```http
Authorization: Bearer your_access_token_here
```

---

## 👤 Patient Endpoints

### Get My Profile

```http
GET /patients/me
Authorization: Bearer {token}
```

### Upload Radiology Image

```http
POST /patients/upload-image
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [image file]
modality: "xray" | "ct" | "mri"
description: "Optional description"
```

**Response**:
```json
{
  "id": 1,
  "patient_id": 1,
  "modality": "xray",
  "image_path": "patient_1/uuid.jpg",
  "upload_date": "2025-12-28T10:00:00",
  "ai_analyzed": false,
  ...
}
```

### Analyze Uploaded Scan

```http
POST /patients/scans/{scan_id}/analyze
Authorization: Bearer {token}
```

**Response**:
```json
{
  "id": 1,
  "ai_analyzed": true,
  "detected_abnormalities": "[\"opacity in right lung\"]",
  "disease_classification": "Pneumonia",
  "confidence_score": 0.85,
  "risk_level": "medium",
  "ai_explanation": "AI detected suspicious opacity...",
  ...
}
```

### Get My Scans

```http
GET /patients/scans?skip=0&limit=20
Authorization: Bearer {token}
```

### Get Scan Details

```http
GET /patients/scans/{scan_id}
Authorization: Bearer {token}
```

### Get My Reports

```http
GET /patients/reports?skip=0&limit=20
Authorization: Bearer {token}
```

### Get Health Summary

```http
GET /patients/health-summary
Authorization: Bearer {token}
```

**Response**:
```json
{
  "patient_id": 1,
  "total_scans": 5,
  "total_reports": 3,
  "summary": "AI-generated comprehensive health summary..."
}
```

---

## 👨‍⚕️ Doctor Endpoints

### Get All Patients

```http
GET /doctors/patients?skip=0&limit=50
Authorization: Bearer {token}
```

**Response**:
```json
[
  {
    "id": 1,
    "username": "patient1",
    "full_name": "John Doe",
    "email": "patient@example.com",
    "total_scans": 3,
    "total_reports": 2,
    "pending_reports": 1
  },
  ...
]
```

### Get Patient's Scans

```http
GET /doctors/patients/{patient_id}/scans
Authorization: Bearer {token}
```

### Get Patient's Reports

```http
GET /doctors/patients/{patient_id}/reports
Authorization: Bearer {token}
```

### Generate AI Report

```http
POST /doctors/generate-report
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": 1,
  "scan_id": 1,
  "report_type": "AI Generated Radiology Report"
}
```

**Response**: MedicalReport object with AI-generated content

### Validate Report

```http
PUT /doctors/reports/{report_id}/validate
Authorization: Bearer {token}
Content-Type: application/json

{
  "doctor_notes": "Confirmed AI findings. Additional observations...",
  "diagnosis": "Pneumonia - Right lower lobe",
  "recommended_treatment": "Antibiotics course, follow-up in 2 weeks",
  "medicine_suggestions": "[{\"name\":\"Amoxicillin\",\"dosage\":\"500mg\"}]",
  "status": "validated"
}
```

**Status values**: `pending`, `validated`, `rejected`

### Get Pending Reports

```http
GET /doctors/pending-reports?skip=0&limit=50
Authorization: Bearer {token}
```

### Suggest Medicines

```http
POST /doctors/suggest-medicines/{patient_id}?disease_classification=Pneumonia&symptoms=Cough,Fever
Authorization: Bearer {token}
```

**Response**:
```json
{
  "medicines": [
    {
      "name": "Amoxicillin",
      "purpose": "Antibiotic for bacterial infections",
      "general_usage": "Take with food, complete full course",
      "precautions": "Avoid if allergic to penicillin"
    }
  ],
  "disclaimer": "Consult healthcare provider before taking..."
}
```

---

## 🤖 AI Service Endpoints

### Chat with AI Assistant

```http
POST /ai/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "What does opacity in lung mean?",
  "session_id": null
}
```

**Response**:
```json
{
  "id": 1,
  "session_id": 1,
  "sender": "ai",
  "message": "Opacity in the lung refers to an area that appears white...",
  "timestamp": "2025-12-28T10:00:00"
}
```

### Chat with AI About Specific Scan

```http
POST /ai/chat/scan
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "Can you explain the findings in my scan?",
  "scan_id": 1,
  "session_id": null
}
```

**Features**:
- AI has access to the specific scan's analysis results
- Provides context-aware responses based on scan findings
- References actual abnormalities, classifications, and risk levels from the scan
- Educational explanations about detected conditions
- Personalized recommendations based on scan modality and results

**Response**:
```json
{
  "id": 2,
  "session_id": 1,
  "sender": "ai",
  "message": "Based on your chest X-ray from 2025-12-29, the AI analysis detected an opacity in the right lower lobe with 85% confidence. This finding, combined with your symptoms, suggests pneumonia. The detected abnormality shows moderate severity. I recommend consulting with your healthcare provider for proper treatment. This scan shows a medium risk level, which means timely medical attention is important...",
  "timestamp": "2025-12-29T10:00:00"
}
```

**Access Control**:
- Patients can only access their own scans
- Doctors can access any patient's scans
- Admins have full access

### Get Chat Sessions

```http
GET /ai/chat/sessions?skip=0&limit=20
Authorization: Bearer {token}
```

### Get Session Messages

```http
GET /ai/chat/sessions/{session_id}/messages
Authorization: Bearer {token}
```

### Classify Disease

```http
POST /ai/classify-disease
Authorization: Bearer {token}
Content-Type: application/json

{
  "symptoms": "Persistent cough, fever, chest pain",
  "medical_history": "Smoker for 10 years",
  "scan_findings": "Opacity in right lower lobe"
}
```

**Response**:
```json
{
  "primary_diagnosis": "Pneumonia",
  "differential_diagnoses": ["Bronchitis", "Lung abscess"],
  "confidence_score": 0.82,
  "severity": "moderate",
  "risk_factors": ["Smoking history", "Chest symptoms"],
  "explanation": "Based on symptoms and findings...",
  "recommended_tests": ["Blood culture", "Sputum test"]
}
```

### Suggest Medicines

```http
POST /ai/suggest-medicines?disease_classification=Pneumonia&symptoms=Cough,Fever&patient_age=45
Authorization: Bearer {token}
```

### Assess Risk

```http
POST /ai/assess-risk
Authorization: Bearer {token}
Content-Type: application/json

{
  "findings": [
    "Opacity in right lung",
    "Elevated white blood cell count",
    "Fever for 3 days"
  ],
  "medical_history": "Type 2 diabetes"
}
```

**Response**:
```json
{
  "overall_risk": "MEDIUM",
  "risk_factors": ["Diabetes", "Lung opacity", "Infection signs"],
  "priority_level": "urgent",
  "recommendations": [
    "Immediate antibiotic therapy",
    "Monitor blood sugar levels",
    "Follow-up scan in 1 week"
  ],
  "explanation": "Patient shows signs of pneumonia with diabetes..."
}
```

---

## 🔧 Admin Endpoints

### List All Users

```http
GET /admin/users?skip=0&limit=100&role=patient
Authorization: Bearer {token}
```

**Query Parameters**:
- `skip`: Pagination offset
- `limit`: Number of results
- `role`: Filter by role (optional)

### Get User Details

```http
GET /admin/users/{user_id}
Authorization: Bearer {token}
```

### Update User Role

```http
PUT /admin/users/{user_id}/role
Authorization: Bearer {token}
Content-Type: application/json

{
  "role": "doctor"
}
```

### Toggle User Active Status

```http
PUT /admin/users/{user_id}/toggle-active
Authorization: Bearer {token}
```

### Delete User

```http
DELETE /admin/users/{user_id}
Authorization: Bearer {token}
```

### Get System Statistics

```http
GET /admin/system-stats
Authorization: Bearer {token}
```

**Response**:
```json
{
  "total_users": 150,
  "total_patients": 120,
  "total_doctors": 25,
  "total_scans": 450,
  "total_reports": 380,
  "pending_reports": 15,
  "ai_analyses_today": 23
}
```

### Get System Logs

```http
GET /admin/logs?skip=0&limit=100&action=USER_LOGIN
Authorization: Bearer {token}
```

### Get Reports Needing Validation

```http
GET /admin/reports/pending-validation?skip=0&limit=50
Authorization: Bearer {token}
```

---

## 📊 Response Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## 🔄 Pagination

Most list endpoints support pagination:

```http
GET /endpoint?skip=0&limit=20
```

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 20)

---

## 🧪 Testing with cURL

### Login Example

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"
```

### Upload Image Example

```bash
curl -X POST "http://localhost:8000/patients/upload-image" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/xray.jpg" \
  -F "modality=xray" \
  -F "description=Chest pain"
```

---

## 🐍 Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "password"}
)
token = response.json()["access_token"]

# Headers with token
headers = {"Authorization": f"Bearer {token}"}

# Upload image
with open("xray.jpg", "rb") as f:
    files = {"file": f}
    data = {"modality": "xray", "description": "Chest scan"}
    response = requests.post(
        f"{BASE_URL}/patients/upload-image",
        headers=headers,
        files=files,
        data=data
    )
    scan = response.json()
    print(f"Scan uploaded: {scan['id']}")

# Analyze scan
response = requests.post(
    f"{BASE_URL}/patients/scans/{scan['id']}/analyze",
    headers=headers
)
analysis = response.json()
print(f"AI Analysis: {analysis['ai_explanation']}")
```

---

## ⚠️ Important Notes

1. **Authentication Required**: Most endpoints require valid JWT token
2. **Role-Based Access**: Endpoints are restricted by user role
3. **File Size Limit**: Maximum upload size is 10MB (configurable)
4. **Accepted Formats**: JPG, JPEG, PNG only
5. **AI Disclaimer**: All AI outputs require professional validation
6. **Rate Limiting**: Consider implementing in production

---

## 📞 Support

For detailed API documentation, visit: http://localhost:8000/docs
