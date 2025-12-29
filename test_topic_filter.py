"""
Test script to verify topic filtering for the AI chat endpoint
"""
from app.utils.topic_validator import TopicValidator

# Test cases
test_messages = [
    # Should be filtered out (non-medical)
    "What is Deep Learning?",
    "How does artificial intelligence work?",
    "What is machine learning?",
    "Tell me about programming",
    "What's the weather like?",
    
    # Should be allowed (medical)
    "What causes chest pain?",
    "I have a headache, what should I do?",
    "What is an X-ray scan?",
    "What are the symptoms of diabetes?",
    "When should I see a doctor?",
    "What is pneumonia?",
    "My back hurts, what could it be?",
    "What is an MRI scan used for?"
]

print("Testing Topic Validator:")
print("=" * 50)

for message in test_messages:
    is_medical = TopicValidator.is_medical_topic(message)
    status = "✅ ALLOWED" if is_medical else "❌ FILTERED"
    print(f"{status}: {message}")

print("\n" + "=" * 50)
print("Redirect message:")
print(TopicValidator.get_redirect_message())
