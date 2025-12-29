# Medicine Suggestion API - Bangladesh Perspective

## Overview
The medicine suggestion API has been enhanced to provide Bangladesh-specific medicine recommendations based on patient scan images and AI analysis.

## API Endpoint
```
POST /doctors/suggest-medicines/{patient_id}
```

## Features
- **Scan-Based Analysis**: Uses patient's radiology scan images for medicine suggestions
- **Bangladesh Context**: Provides medicine recommendations available in Bangladesh pharmacies
- **AI-Powered**: Leverages Gemini AI for intelligent analysis and suggestions
- **Multi-Modal Support**: Works with X-Ray, CT, and MRI scans

## Parameters

### Path Parameters
- `patient_id` (int, required): ID of the patient

### Query Parameters
- `scan_id` (int, optional): Specific scan to analyze. If not provided, uses latest scan
- `disease_classification` (str, optional): Manual disease classification. If not provided, uses AI analysis
- `symptoms` (str, optional): Patient symptoms description

## Request Examples

### 1. Basic Usage (Using Latest Scan)
```bash
POST /doctors/suggest-medicines/123
Authorization: Bearer <doctor_token>
```

### 2. With Specific Scan
```bash
POST /doctors/suggest-medicines/123?scan_id=456
Authorization: Bearer <doctor_token>
```

### 3. With Manual Classification
```bash
POST /doctors/suggest-medicines/123?disease_classification=Pneumonia&symptoms=Cough%20and%20fever
Authorization: Bearer <doctor_token>
```

## Response Format

```json
{
  "medicines": [
    {
      "name": "Paracetamol (Napa, Ace)",
      "generic_name": "Paracetamol",
      "bangladesh_brands": ["Napa", "Ace", "Fast"],
      "purpose": "Fever reduction and pain relief",
      "general_usage": "500mg 1-2 times daily as needed",
      "precautions": "Do not exceed 4g daily, avoid with liver disease",
      "availability": "OTC",
      "approximate_cost": "5-15 BDT per strip"
    },
    {
      "name": "Azithromycin (Azithral, Zithromax)",
      "generic_name": "Azithromycin",
      "bangladesh_brands": ["Azithral", "Zithromax", "Azid"],
      "purpose": "Bacterial infection treatment",
      "general_usage": "500mg once daily for 3-5 days",
      "precautions": "Complete full course, check allergies",
      "availability": "Prescription required",
      "approximate_cost": "150-300 BDT per course"
    }
  ],
  "lifestyle_recommendations": [
    "Drink plenty of water (especially important in Bangladesh's hot climate)",
    "Avoid crowded places during respiratory infections",
    "Take medicines after meals to reduce stomach irritation"
  ],
  "follow_up": "Follow up in 3-5 days or if symptoms worsen",
  "disclaimer": "This is AI-generated advice. Please consult with a registered medical practitioner in Bangladesh before taking any medicines.",
  "scan_context": {
    "scan_id": 456,
    "modality": "xray",
    "upload_date": "2025-12-29T10:30:00",
    "analyzed": true,
    "classification": "Pneumonia",
    "risk_level": "medium"
  },
  "patient_context": {
    "patient_id": 123,
    "name": "Patient Name",
    "age": 35
  }
}
```

## Bangladesh-Specific Features

### 1. Local Pharmaceutical Brands
- Includes major Bangladesh pharmaceutical companies (Square, Beximco, Incepta, ACI, etc.)
- Shows both generic names and local brand names
- Provides approximate costs in Bangladesh Taka (BDT)

### 2. Climate Considerations
- Takes into account Bangladesh's tropical climate
- Considers common health issues in the region
- Provides climate-appropriate lifestyle recommendations

### 3. Healthcare Infrastructure
- Considers medicine availability in local pharmacies
- Distinguishes between OTC and prescription medicines
- Provides realistic pricing in BDT

### 4. Cultural Context
- Medicine timing recommendations based on local meal patterns
- Considers traditional/herbal alternatives where appropriate
- Emphasizes consultation with local healthcare providers

## Additional Helper Endpoints

### Get Available Scans for Medicine Suggestions
```
GET /doctors/patients/{patient_id}/scans-for-medicine
```

Returns list of patient scans with analysis status, useful for selecting which scan to use for medicine suggestions.

## Workflow

1. **Patient Upload**: Patient uploads scan image
2. **AI Analysis**: System analyzes scan for abnormalities (if not already done)
3. **Medicine Suggestion**: Doctor requests medicine suggestions using this API
4. **Bangladesh Context**: AI provides locally relevant medicine recommendations
5. **Doctor Validation**: Doctor reviews and validates suggestions before prescribing

## Error Handling

- `403`: Non-doctor users attempting access
- `404`: Patient not found or no scans available
- `400`: Missing required parameters
- `500`: AI analysis failures

## Security

- Requires doctor-level authentication
- Validates patient-doctor relationship
- Logs all medicine suggestion requests for audit

## Bangladesh Healthcare Compliance

- Emphasizes consultation with registered local doctors
- Follows Bangladesh pharmaceutical naming conventions
- Considers local drug availability and pricing
- Includes appropriate medical disclaimers
