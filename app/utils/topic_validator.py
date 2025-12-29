"""
Topic validation utilities for the AI chat system.
Ensures chat remains focused on radiology and healthcare topics.
"""
import re
from typing import List


class TopicValidator:
    """Validator to check if messages are related to radiology and healthcare."""
    
    # Healthcare and radiology related keywords
    HEALTHCARE_KEYWORDS = [
        # Medical imaging
        'x-ray', 'xray', 'ct', 'mri', 'ultrasound', 'scan', 'imaging', 'radiology',
        'mammography', 'fluoroscopy', 'angiography', 'pet', 'tomography',
        
        # Medical conditions
        'disease', 'condition', 'diagnosis', 'symptom', 'pain', 'treatment',
        'therapy', 'medicine', 'medication', 'drug', 'prescription', 'doctor',
        'physician', 'nurse', 'hospital', 'clinic', 'patient', 'health',
        
        # Body parts and anatomy
        'heart', 'lung', 'brain', 'kidney', 'liver', 'bone', 'muscle', 'blood',
        'chest', 'abdomen', 'head', 'neck', 'spine', 'joint', 'organ',
        
        # Medical procedures
        'surgery', 'operation', 'biopsy', 'injection', 'examination', 'checkup',
        'consultation', 'screening', 'test', 'analysis', 'report',
        
        # Common medical terms
        'fever', 'headache', 'nausea', 'fatigue', 'infection', 'inflammation',
        'tumor', 'cancer', 'diabetes', 'hypertension', 'allergy', 'fracture'
    ]
    
    # Non-medical topics that should be filtered out
    NON_MEDICAL_KEYWORDS = [
        # Technology and general science
        'weather', 'sports', 'politics', 'entertainment', 'movies', 'music',
        'games', 'fashion', 'food', 'cooking', 'travel', 'technology',
        'programming', 'software', 'computer', 'internet', 'social media',
        'artificial intelligence', 'ai', 'machine learning', 'deep learning',
        'data science', 'algorithms', 'neural networks', 'python', 'javascript',
        'coding', 'development', 'database', 'server', 'cloud computing',
        
        # General education/science not medical
        'mathematics', 'physics', 'chemistry', 'biology', 'history',
        'geography', 'literature', 'philosophy', 'economics', 'business',
        'finance', 'marketing', 'sales', 'management', 'accounting',
        
        # Entertainment and lifestyle
        'celebrity', 'news', 'current events', 'shopping', 'fashion',
        'beauty', 'makeup', 'hair', 'style', 'trends', 'gossip'
    ]
    
    @classmethod
    def is_medical_topic(cls, message: str) -> bool:
        """
        Check if a message is related to medical/healthcare topics.
        Uses strict filtering to only allow direct medical questions.
        
        Args:
            message: The message to validate
            
        Returns:
            bool: True if the message appears to be medical-related
        """
        if not message:
            return False
            
        message_lower = message.lower()
        
        # Check for non-medical keywords first (strict filtering)
        non_medical_score = sum(1 for keyword in cls.NON_MEDICAL_KEYWORDS 
                               if keyword in message_lower)
        
        # If any non-medical keywords found, it's likely not a medical question
        if non_medical_score > 0:
            return False
        
        # Check for healthcare keywords
        healthcare_score = sum(1 for keyword in cls.HEALTHCARE_KEYWORDS 
                             if keyword in message_lower)
        
        # Only allow if there are clear medical keywords
        if healthcare_score > 0:
            return True
        
        # For questions that might be medical but don't have clear keywords,
        # check if they're asking about symptoms or health concerns
        question_patterns = [
            'what is', 'what are', 'how to', 'why do', 'when should',
            'i have', 'i feel', 'my', 'hurts', 'pain', 'ache', 'sick',
            'doctor', 'medicine', 'treatment', 'cure', 'heal'
        ]
        
        has_question_pattern = any(pattern in message_lower for pattern in question_patterns)
        
        # Be very conservative - only allow if it clearly looks like a medical question
        return has_question_pattern and len(message.split()) >= 3  # At least 3 words
    
    @classmethod
    def get_redirect_message(cls) -> str:
        """
        Get the standard message to redirect non-medical topics.
        
        Returns:
            str: Redirect message
        """
        return ("I'm a specialized medical AI assistant focused on radiology and healthcare topics. "
                "I can help you with medical questions, radiology image analysis, symptoms discussion, "
                "and healthcare guidance. How can I assist you with a medical or radiology-related question?")
