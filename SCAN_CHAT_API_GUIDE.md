# Scan-Specific AI Chat API Documentation

## Overview

The new `/ai/chat/scan` endpoint allows users to have context-aware conversations with the AI assistant about specific radiology scans. Unlike the general chat endpoint, this specialized endpoint provides the AI with access to the scan's analysis results, enabling more personalized and accurate responses.

## Endpoint Details

**URL:** `POST /ai/chat/scan`
**Authentication:** Bearer Token Required
**Content-Type:** application/json

## Features

- **Context-Aware Responses**: AI has access to specific scan analysis results
- **Personalized Insights**: Responses tailored to actual scan findings
- **Educational**: Explains medical terms and conditions found in the scan
- **Safety-First**: Includes appropriate medical disclaimers and encourages professional consultation
- **Session Continuity**: Maintains conversation history for follow-up questions

## Request Schema

```json
{
  "message": "string (1-5000 characters)",
  "scan_id": "integer (required)",
  "session_id": "integer (optional)"
}
```

## Access Control

- **Patients**: Can only access their own scans
- **Doctors**: Can access any patient's scans  
- **Admins**: Full access to all scans

## Usage Examples

### 1. Initial Question About Scan

```http
POST /ai/chat/scan
Authorization: Bearer {token}

{
  "message": "Can you explain what was found in my scan?",
  "scan_id": 123,
  "session_id": null
}
```

**Response:**
```json
{
  "id": 1,
  "session_id": 1,
  "sender": "ai",
  "message": "Based on your chest X-ray from December 29, 2025, our AI analysis detected an opacity in the right lower lobe with 85% confidence. This finding suggests pneumonia, which is an infection of the lung tissue. The detected abnormality shows moderate severity with a medium risk level.\n\nWhat this means:\n- An opacity appears as a white or cloudy area on the X-ray\n- It indicates inflammation or infection in that part of the lung\n- The 85% confidence score shows this finding is quite reliable\n\nNext steps I recommend:\n1. Consult with your healthcare provider promptly\n2. Discuss treatment options, likely antibiotics\n3. Follow-up imaging may be needed\n\n⚠️ Important: This is AI analysis for educational purposes. Please consult your healthcare provider for proper diagnosis and treatment.",
  "timestamp": "2025-12-29T10:00:00"
}
```

### 2. Follow-up Question in Same Session

```http
POST /ai/chat/scan
Authorization: Bearer {token}

{
  "message": "Is this condition serious? Should I be worried?",
  "scan_id": 123,
  "session_id": 1
}
```

**Response:**
```json
{
  "id": 2,
  "session_id": 1,
  "sender": "ai",
  "message": "Based on your scan results, this appears to be a moderate case of pneumonia, which is treatable but requires prompt medical attention.\n\nRisk Assessment:\n- Your scan shows medium risk level\n- Pneumonia can be serious if left untreated\n- Early treatment typically leads to good outcomes\n- The opacity is localized to one area (right lower lobe)\n\nWhy you should seek care promptly:\n1. Pneumonia can worsen without treatment\n2. Early antibiotics are most effective\n3. Monitoring prevents complications\n\nPositive factors:\n- The finding is well-defined on imaging\n- Localized to one lung area\n- AI detected it clearly for early intervention\n\n⚠️ Please don't delay in contacting your healthcare provider. While pneumonia is very treatable, prompt medical care is important for the best outcome.",
  "timestamp": "2025-12-29T10:05:00"
}
```

### 3. Question About Treatment

```http
POST /ai/chat/scan
Authorization: Bearer {token}

{
  "message": "What kind of treatment will I need?",
  "scan_id": 123,
  "session_id": 1
}
```

## Error Responses

### Scan Not Found
```json
{
  "detail": "Scan not found"
}
```
**Status Code:** 404

### Access Denied
```json
{
  "detail": "Access denied to this scan"
}
```
**Status Code:** 403

### Empty Message
```json
{
  "detail": "Message cannot be empty"
}
```
**Status Code:** 400

## Differences from Regular Chat

| Feature | Regular Chat (`/ai/chat`) | Scan Chat (`/ai/chat/scan`) |
|---------|---------------------------|----------------------------|
| Context | General medical knowledge | Specific scan analysis results |
| Responses | Generic medical information | Personalized to scan findings |
| Requirements | Message only | Message + scan_id |
| Access | Any authenticated user | Scan owner + doctors/admins |
| Use Cases | General medical questions | Scan-specific consultations |

## Implementation Notes

### For Developers

1. **Validation**: The endpoint validates scan ownership before processing
2. **Error Handling**: Graceful degradation if AI service fails
3. **Logging**: All requests logged with scan_id for audit
4. **Session Management**: Automatic session creation and continuation

### For Frontend Integration

```javascript
// Example JavaScript integration
async function chatAboutScan(message, scanId, sessionId = null) {
  const response = await fetch('/ai/chat/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({
      message: message,
      scan_id: scanId,
      session_id: sessionId
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}
```

## Best Practices

1. **Always show scan context** to users (scan date, modality, etc.)
2. **Include medical disclaimers** prominently in UI
3. **Suggest professional consultation** after AI responses
4. **Handle errors gracefully** with user-friendly messages
5. **Track session continuity** for better conversations

## Security Considerations

- Scan access is strictly controlled by ownership and roles
- All requests are logged for audit purposes
- No scan data is exposed to unauthorized users
- Medical disclaimers are included in all responses
