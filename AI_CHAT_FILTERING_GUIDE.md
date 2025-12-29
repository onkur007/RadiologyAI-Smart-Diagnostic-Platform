# AI Chat Endpoint Filtering Behavior

## Expected Behavior After Updates

### Request Example:
```json
{
  "message": "What is Deep Learning?",
  "session_id": 5
}
```

### Expected Response:
```json
{
    "id": 8,
    "session_id": 2,
    "sender": "ai",
    "message": "I'm a specialized medical AI assistant focused on radiology and healthcare topics. I can help you with:\n\n• Medical symptoms and conditions\n• Radiology and medical imaging questions\n• Treatment options and medications\n• When to seek medical care\n• Health and wellness guidance\n\nHow can I assist you with a medical or health-related question today?",
    "timestamp": "2025-12-29T03:55:56.762155"
}
```

## Filtering Logic

### Two-Layer Filtering:

1. **Keyword-Based Pre-filtering (TopicValidator)**:
   - Checks for non-medical keywords like "deep learning", "artificial intelligence", "programming"
   - If found, the topic is likely non-medical
   - Only allows messages with clear medical keywords or health-related question patterns

2. **AI-Powered Topic Analysis**:
   - Uses Gemini AI to analyze the message context
   - Strict prompt that refuses technology, education, or general science topics
   - Only allows direct patient care, symptoms, medical conditions, and treatments

### Topics That Will Be FILTERED OUT:
- ❌ "What is Deep Learning?"
- ❌ "How does AI work?"
- ❌ "What is machine learning?"
- ❌ "Tell me about programming"
- ❌ "What's the weather?"
- ❌ "How to code in Python?"

### Topics That Will Be ALLOWED:
- ✅ "What causes chest pain?"
- ✅ "I have a headache"
- ✅ "What is an X-ray?"
- ✅ "Symptoms of diabetes"
- ✅ "When to see a doctor?"
- ✅ "What is pneumonia?"
- ✅ "My back hurts"

### Updated Prompt Strategy:
The AI now receives explicit instructions to:
- REFUSE general technology topics
- ONLY discuss patient symptoms, medical conditions, treatments
- Provide polite redirects for non-medical topics
- Focus strictly on healthcare and radiology

### Benefits:
1. Prevents misuse of the medical AI for general education
2. Keeps conversations focused on healthcare
3. Maintains the system's medical purpose
4. Provides clear guidance to users about appropriate topics
5. Better serves patients with genuine medical questions
