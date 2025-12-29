# Patient Risk Profiling API - Bangladesh Healthcare Context

## Overview
The patient risk profiling system provides AI-powered health risk assessment based on radiology scans, specifically designed for Bangladesh healthcare context.

## Features
- **Comprehensive Risk Profiling**: Analyzes all patient scans for overall health assessment
- **Latest Scan Risk Check**: Quick assessment based on most recent scan
- **Bangladesh-Specific Insights**: Considers local environmental and health factors
- **Progressive Analysis**: Tracks changes over time with multiple scans
- **Actionable Recommendations**: Provides specific next steps and monitoring advice

## API Endpoints

### 1. Comprehensive Risk Profile
```
GET /patients/risk-profile
```
Analyzes all patient scans to provide comprehensive risk assessment.

#### Features:
- Analyzes all uploaded scans
- Automatically analyzes unanalyzed scans (up to 3 most recent)
- Provides overall risk stratification
- Tracks progressive changes over time
- Bangladesh-specific health recommendations

#### Response Example:
```json
{
  "patient_info": {
    "name": "Patient Name",
    "patient_id": 123,
    "age": 35,
    "total_scans": 5,
    "analyzed_scans": 3
  },
  "risk_summary": {
    "overall_risk_level": "MEDIUM",
    "confidence_score": 78.5,
    "total_scans_analyzed": 3,
    "total_abnormalities_detected": 2,
    "unique_abnormality_types": 1,
    "disease_classifications": ["Pneumonia", "Normal"]
  },
  "scan_breakdown": [
    {
      "scan_id": 456,
      "modality": "xray",
      "date": "2025-12-29T10:30:00",
      "disease_classification": "Pneumonia",
      "risk_level": "MEDIUM",
      "confidence_score": 85.0,
      "abnormalities": [
        {
          "type": "opacity",
          "location": "right lower lobe",
          "severity": "moderate"
        }
      ],
      "explanation": "Consolidation in right lower lobe suggestive of pneumonia"
    }
  ],
  "ai_risk_assessment": {
    "overall_risk_assessment": {
      "primary_concerns": ["Respiratory infection", "Recurrent pneumonia risk"],
      "risk_factors": ["Previous lung infection", "Environmental exposure"],
      "progressive_changes": "Improvement noted from previous scan",
      "critical_findings": []
    },
    "health_outlook": {
      "short_term_prognosis": "Good with proper treatment",
      "long_term_prognosis": "Excellent with lifestyle modifications",
      "preventive_measures": ["Annual chest X-rays", "Vaccination"],
      "lifestyle_modifications": ["Avoid polluted areas", "Regular exercise"]
    },
    "monitoring_recommendations": {
      "follow_up_frequency": "3-6 months",
      "specific_tests": ["Complete blood count", "Pulmonary function test"],
      "warning_signs": ["Persistent cough", "Chest pain", "Shortness of breath"],
      "emergency_indicators": ["High fever", "Severe breathing difficulty"]
    },
    "bangladesh_context": {
      "environmental_factors": ["Air pollution in Dhaka", "Monsoon humidity effects"],
      "seasonal_considerations": ["Higher infection risk during monsoon"],
      "local_healthcare_recommendations": ["Consult pulmonologist at BIRDEM or Square Hospital"],
      "dietary_considerations": ["Increase vitamin C intake", "Traditional honey and ginger"]
    },
    "confidence_assessment": {
      "analysis_reliability": "78%",
      "data_completeness": "Good",
      "recommendation_strength": "Moderate to Strong"
    },
    "summary": "Patient shows signs of respiratory condition with moderate risk level requiring monitoring"
  },
  "recommendations": {
    "follow_up_required": true,
    "urgent_consultation": false,
    "routine_monitoring": false,
    "next_scan_timeline": "3-6 months"
  },
  "unanalyzed_scans": 2,
  "generated_at": "2025-12-29T15:30:00"
}
```

### 2. Latest Scan Risk Assessment
```
GET /patients/latest-scan-risk
```
Quick risk assessment based on patient's most recent scan.

#### Features:
- Analyzes only the latest scan
- Provides immediate risk interpretation
- Quick actionable recommendations
- Simplified response format

#### Response Example:
```json
{
  "scan_info": {
    "scan_id": 456,
    "modality": "xray",
    "upload_date": "2025-12-29T10:30:00",
    "description": "Chest X-ray for cough"
  },
  "risk_assessment": {
    "risk_level": "MEDIUM",
    "confidence_score": 85.0,
    "disease_classification": "Pneumonia",
    "interpretation": {
      "description": "Moderate risk detected",
      "meaning": "Some abnormalities found that require attention and monitoring.",
      "action": "Schedule follow-up with healthcare provider within 2-4 weeks",
      "urgency": "Moderate"
    }
  },
  "findings": {
    "total_abnormalities": 1,
    "abnormalities": [
      {
        "type": "opacity",
        "location": "right lower lobe",
        "severity": "moderate"
      }
    ],
    "ai_explanation": "Consolidation in right lower lobe suggestive of pneumonia"
  },
  "recommendations": {
    "immediate_action": "Schedule follow-up with healthcare provider within 2-4 weeks",
    "follow_up_timeline": "1-3 months",
    "lifestyle_tips": [
      "Maintain a healthy diet with plenty of fruits and vegetables",
      "Stay hydrated, especially in Bangladesh's climate",
      "Regular exercise as appropriate for your condition",
      "Avoid smoking and limit alcohol consumption",
      "Follow up with healthcare providers as recommended"
    ]
  },
  "next_steps": {
    "complete_risk_profile": "Get comprehensive risk profile at /patients/risk-profile",
    "consult_doctor": "Book appointment for detailed consultation",
    "monitor_symptoms": "Watch for any new or worsening symptoms"
  },
  "generated_at": "2025-12-29T15:30:00"
}
```

## Risk Level Classifications

### LOW Risk
- **Description**: No significant abnormalities detected
- **Action**: Routine monitoring and regular check-ups
- **Timeline**: Follow up in 6-12 months
- **Urgency**: Routine

### MEDIUM Risk
- **Description**: Some abnormalities requiring attention
- **Action**: Schedule follow-up within 2-4 weeks
- **Timeline**: Follow up in 1-3 months
- **Urgency**: Moderate priority

### HIGH Risk
- **Description**: Significant findings requiring immediate attention
- **Action**: Consult doctor immediately
- **Timeline**: Follow up in 1-2 weeks
- **Urgency**: High priority

## Bangladesh-Specific Features

### Environmental Considerations
- **Air Pollution**: Dhaka and urban area pollution effects
- **Climate**: Monsoon humidity and respiratory health
- **Seasonal Risks**: Increased infection risks during certain seasons

### Healthcare Integration
- **Local Hospitals**: References to major Bangladesh hospitals
- **Traditional Medicine**: Integration with local remedies where appropriate
- **Cost Considerations**: Awareness of healthcare accessibility

### Cultural Context
- **Dietary Recommendations**: Bangladesh food and nutrition context
- **Lifestyle Factors**: Local living conditions and health practices
- **Family Health**: Community and family health considerations

## Workflow

1. **Scan Upload**: Patient uploads radiology scan
2. **Automatic Analysis**: System analyzes scan if not already done
3. **Risk Assessment**: AI generates risk profile based on findings
4. **Bangladesh Context**: Adds local health considerations
5. **Recommendations**: Provides actionable next steps
6. **Monitoring**: Tracks changes over time with multiple scans

## Security & Privacy

- **Patient-Only Access**: Only the scan owner can access their risk profile
- **Data Protection**: All health data is securely stored and processed
- **Audit Logging**: All risk assessments are logged for tracking

## Error Handling

- **No Scans**: Clear message prompting scan upload
- **Analysis Failure**: Graceful degradation with manual options
- **Partial Data**: Works with incomplete scan analysis
- **Network Issues**: Robust retry mechanisms

## Integration Points

- **Doctor Consultation**: Links to doctor medicine suggestion API
- **Report Generation**: Connects with medical report system
- **Chat Support**: Integration with AI health chat features

## Usage Guidelines

### For Patients
1. Upload high-quality scan images
2. Use latest scan risk for immediate insights
3. Use comprehensive profile for detailed assessment
4. Follow recommendations and seek professional consultation

### For Healthcare Providers
- Use risk profiles to prioritize patient care
- Reference Bangladesh-specific recommendations
- Integrate with existing consultation workflows
- Monitor patient progression over time

## Limitations & Disclaimers

- **AI Assistance**: All assessments are AI-generated and require medical validation
- **Professional Consultation**: Always emphasizes need for professional medical advice
- **Local Healthcare**: Recommends consultation with registered Bangladesh physicians
- **Emergency Care**: Clear guidance for emergency medical situations
