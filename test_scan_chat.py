#!/usr/bin/env python3
"""
Test script for the new scan-specific AI chat endpoint.
Demonstrates how to chat with AI about specific radiology scan findings.
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "admin"  # Change to your test user
TEST_PASSWORD = "password"  # Change to your test password

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def test_scan_chat():
    """Test the scan-specific chat endpoint"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Get available scans for the user
    print("1. Fetching available scans...")
    scans_response = requests.get(f"{BASE_URL}/patients/scans", headers=headers)
    
    if scans_response.status_code != 200:
        print(f"Failed to get scans: {scans_response.text}")
        return
    
    scans = scans_response.json()
    if not scans:
        print("No scans found. Please upload a scan first using /patients/upload-image")
        return
    
    # Use the first available scan
    scan = scans[0]
    scan_id = scan["id"]
    print(f"Using scan ID: {scan_id}")
    print(f"Scan details: {scan['modality']} from {scan['upload_date']}")
    print(f"AI analyzed: {scan['ai_analyzed']}")
    
    if scan['ai_analyzed']:
        print(f"Disease classification: {scan.get('disease_classification', 'Unknown')}")
        print(f"Risk level: {scan.get('risk_level', 'Unknown')}")
        print(f"Confidence: {scan.get('confidence_score', 'Unknown')}")
    
    # Step 2: Test scan-specific chat
    test_messages = [
        "Can you explain the findings in my scan?",
        "What does this mean for my health?",
        "What should I do next?",
        "Is this condition serious?"
    ]
    
    session_id = None
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing message: '{message}'")
        
        chat_data = {
            "message": message,
            "scan_id": scan_id,
            "session_id": session_id
        }
        
        chat_response = requests.post(
            f"{BASE_URL}/ai/chat/scan",
            headers=headers,
            json=chat_data
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            session_id = response_data["session_id"]  # Keep the session for subsequent messages
            
            print(f"✅ Success! Session ID: {session_id}")
            print(f"AI Response: {response_data['message'][:200]}...")
            print(f"Full response length: {len(response_data['message'])} characters")
        else:
            print(f"❌ Failed: {chat_response.status_code}")
            print(f"Error: {chat_response.text}")
            break
    
    # Step 3: Compare with regular chat
    print(f"\n5. Testing regular chat for comparison...")
    regular_chat_data = {
        "message": "What does lung opacity mean?",
        "session_id": None
    }
    
    regular_response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers=headers,
        json=regular_chat_data
    )
    
    if regular_response.status_code == 200:
        print("✅ Regular chat response:")
        print(regular_response.json()["message"][:200] + "...")
    else:
        print(f"❌ Regular chat failed: {regular_response.text}")

def test_access_control():
    """Test access control for scan chat"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n6. Testing access control with non-existent scan...")
    chat_data = {
        "message": "Test message",
        "scan_id": 99999,  # Non-existent scan
        "session_id": None
    }
    
    response = requests.post(
        f"{BASE_URL}/ai/chat/scan",
        headers=headers,
        json=chat_data
    )
    
    if response.status_code == 404:
        print("✅ Access control working: 404 for non-existent scan")
    else:
        print(f"❌ Unexpected response: {response.status_code}")

if __name__ == "__main__":
    print("Testing Scan-Specific AI Chat Endpoint")
    print("="*50)
    
    try:
        test_scan_chat()
        test_access_control()
        print("\n✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
