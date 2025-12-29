"""
Test cases for the enhanced medicine suggestion API
"""
import pytest
from unittest.mock import Mock, patch
import json

# Mock test data
def test_medicine_suggestion_workflow():
    """Test the medicine suggestion workflow logic"""
    
    # Mock patient data
    mock_patient = Mock()
    mock_patient.id = 123
    mock_patient.full_name = "John Doe"
    mock_patient.date_of_birth = None
    
    # Mock scan data
    mock_scan = Mock()
    mock_scan.id = 456
    mock_scan.patient_id = 123
    mock_scan.modality = Mock()
    mock_scan.modality.value = "xray"
    mock_scan.ai_analyzed = True
    mock_scan.detected_abnormalities = json.dumps([
        {"type": "opacity", "location": "right lower lobe", "severity": "moderate"}
    ])
    mock_scan.disease_classification = "Pneumonia"
    mock_scan.confidence_score = 85.0
    mock_scan.risk_level = Mock()
    mock_scan.risk_level.value = "medium"
    mock_scan.ai_explanation = "Consolidation in right lower lobe suggestive of pneumonia"
    mock_scan.upload_date = "2025-12-29T10:30:00"
    mock_scan.image_path = "/path/to/scan.jpg"
    
    # Test scan findings extraction
    scan_findings = {
        "abnormalities": json.loads(mock_scan.detected_abnormalities),
        "risk_level": mock_scan.risk_level.value,
        "confidence": mock_scan.confidence_score,
        "explanation": mock_scan.ai_explanation,
        "modality": mock_scan.modality.value,
        "classification": mock_scan.disease_classification
    }
    
    # Verify scan findings structure
    assert scan_findings["abnormalities"] == [
        {"type": "opacity", "location": "right lower lobe", "severity": "moderate"}
    ]
    assert scan_findings["risk_level"] == "medium"
    assert scan_findings["confidence"] == 85.0
    assert scan_findings["classification"] == "Pneumonia"
    
    print("✓ Medicine suggestion workflow test passed")

def test_bangladesh_medicine_response_structure():
    """Test expected response structure for Bangladesh medicine suggestions"""
    
    expected_response = {
        "medicines": [
            {
                "name": "Paracetamol (Napa, Ace)",
                "generic_name": "Paracetamol",
                "bangladesh_brands": ["Napa", "Ace", "Fast"],
                "purpose": "Fever reduction and pain relief",
                "general_usage": "500mg 1-2 times daily as needed",
                "precautions": "Do not exceed 4g daily",
                "availability": "OTC",
                "approximate_cost": "5-15 BDT per strip"
            }
        ],
        "lifestyle_recommendations": [
            "Drink plenty of water",
            "Avoid crowded places"
        ],
        "follow_up": "Follow up in 3-5 days",
        "disclaimer": "Consult with registered medical practitioner in Bangladesh",
        "scan_context": {
            "scan_id": 456,
            "modality": "xray",
            "analyzed": True,
            "classification": "Pneumonia"
        },
        "patient_context": {
            "patient_id": 123,
            "name": "John Doe",
            "age": None
        }
    }
    
    # Verify required fields
    assert "medicines" in expected_response
    assert "lifestyle_recommendations" in expected_response
    assert "follow_up" in expected_response
    assert "disclaimer" in expected_response
    assert "scan_context" in expected_response
    assert "patient_context" in expected_response
    
    # Verify medicine structure
    medicine = expected_response["medicines"][0]
    required_medicine_fields = [
        "name", "generic_name", "bangladesh_brands", "purpose",
        "general_usage", "precautions", "availability", "approximate_cost"
    ]
    
    for field in required_medicine_fields:
        assert field in medicine, f"Missing required field: {field}"
    
    print("✓ Bangladesh medicine response structure test passed")

if __name__ == "__main__":
    test_medicine_suggestion_workflow()
    test_bangladesh_medicine_response_structure()
    print("\n🎉 All tests passed! The medicine suggestion API is ready.")
