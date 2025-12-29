"""
Gemini AI integration service.
Handles all AI-related operations using Google's Gemini API.
"""
import google.generativeai as genai
from typing import Dict, Optional, List
import json
from PIL import Image

from app.config import settings
from app.models import ImageModality, RiskLevel

# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)


class GeminiAIService:
    """Service class for Gemini AI operations"""
    
    def __init__(self):
        """Initialize Gemini models"""
        self.text_model = genai.GenerativeModel('gemini-2.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def analyze_radiology_image(
        self,
        image_path: str,
        modality: ImageModality,
        patient_context: Optional[str] = None
    ) -> Dict:
        """
        Analyze a radiology image using Gemini Vision API.
        
        Args:
            image_path: Path to the image file
            modality: Type of scan (XRAY, CT, MRI)
            patient_context: Optional patient medical history
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Load image
            img = Image.open(image_path)
            
            # Construct detailed prompt
            prompt = f"""
            You are an expert radiologist AI assistant. Analyze this {modality.value.upper()} scan image.
            
            Please provide:
            1. Detailed description of visible anatomical structures
            2. Any abnormalities or suspicious findings detected
            3. Possible disease classification or conditions
            4. Confidence level (0.0 to 1.0)
            5. Risk assessment (LOW, MEDIUM, HIGH)
            6. Recommendations for further investigation
            
            {f"Patient Context: {patient_context}" if patient_context else ""}
            
            Provide response in the following JSON format:
            {{
                "description": "detailed anatomical description",
                "abnormalities": ["list of abnormalities found"],
                "disease_classification": "primary suspected condition",
                "confidence_score": 0.0-1.0,
                "risk_level": "LOW/MEDIUM/HIGH",
                "explanation": "detailed medical explanation",
                "recommendations": ["list of recommendations"]
            }}
            
            IMPORTANT: Be thorough but always include medical disclaimer that this is AI-assisted analysis 
            and requires professional validation.
            """
            
            # Generate content
            response = self.vision_model.generate_content([prompt, img])
            
            # Parse response
            result = self._parse_ai_response(response.text)
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "description": "AI analysis failed",
                "abnormalities": [],
                "disease_classification": "Unknown",
                "confidence_score": 0.0,
                "risk_level": "MEDIUM",
                "explanation": f"Error during analysis: {str(e)}",
                "recommendations": ["Manual review required"]
            }
    
    async def classify_disease(
        self,
        symptoms: str,
        medical_history: Optional[str] = None,
        scan_findings: Optional[str] = None
    ) -> Dict:
        """
        Classify disease based on symptoms and medical data.
        
        Args:
            symptoms: Patient symptoms description
            medical_history: Optional patient medical history
            scan_findings: Optional radiology scan findings
            
        Returns:
            Dict with disease classification
        """
        try:
            prompt = f"""
            As a medical AI assistant, analyze the following patient information and provide disease classification:
            
            Symptoms: {symptoms}
            {f"Medical History: {medical_history}" if medical_history else ""}
            {f"Scan Findings: {scan_findings}" if scan_findings else ""}
            
            Provide analysis in JSON format:
            {{
                "primary_diagnosis": "most likely condition",
                "differential_diagnoses": ["other possible conditions"],
                "confidence_score": 0.0-1.0,
                "severity": "mild/moderate/severe",
                "risk_factors": ["identified risk factors"],
                "explanation": "detailed medical explanation",
                "recommended_tests": ["additional tests needed"]
            }}
            
            Include appropriate medical disclaimers.
            """
            
            response = self.text_model.generate_content(prompt)
            result = self._parse_ai_response(response.text)
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "primary_diagnosis": "Analysis incomplete",
                "explanation": f"Error: {str(e)}"
            }
    
    async def generate_medical_report(
        self,
        patient_info: Dict,
        scan_info: Dict,
        ai_findings: Dict
    ) -> str:
        """
        Generate structured medical report.
        
        Args:
            patient_info: Patient details
            scan_info: Scan information
            ai_findings: AI analysis results
            
        Returns:
            Formatted medical report text
        """
        try:
            prompt = f"""
            Generate a professional medical radiology report based on:
            
            Patient Information:
            {json.dumps(patient_info, indent=2)}
            
            Scan Information:
            {json.dumps(scan_info, indent=2)}
            
            AI Findings:
            {json.dumps(ai_findings, indent=2)}
            
            Generate a structured medical report with:
            1. Patient Demographics
            2. Examination Details
            3. Clinical Indication
            4. Findings
            5. Impression
            6. Recommendations
            
            Use professional medical terminology and standard report format.
            Include disclaimer that AI-generated content requires physician validation.
            """
            
            response = self.text_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Report generation failed: {str(e)}"
    
    async def chat_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate chatbot response focused only on radiology and healthcare topics.
        
        Args:
            user_message: User's message
            conversation_history: Previous messages for context
            
        Returns:
            AI response text
        """
        try:
            # Check if the message is related to radiology/healthcare using strict filtering
            topic_check_prompt = f"""
            You are a strict medical topic filter. Analyze this message: "{user_message}"
            
            Reply with "NOT_RELEVANT" if the message is about:
            - General technology topics (AI, machine learning, deep learning, programming, etc.)
            - Non-medical sciences (physics, chemistry, mathematics, etc.)
            - Entertainment, sports, politics, news, weather
            - General conversation, greetings, jokes
            - Education topics not directly related to patient care
            - Business, finance, travel, food (unless directly medical)
            - Any topic that is NOT directly about patient symptoms, medical conditions, treatments, or radiology
            
            Reply with "RELEVANT" ONLY if the message is specifically about:
            - Patient symptoms ("I have chest pain", "What causes headaches?")
            - Medical conditions or diseases ("What is diabetes?", "Tell me about pneumonia")
            - Radiology or medical imaging ("What is an X-ray?", "MRI scan results")
            - Medical treatments or procedures ("How is surgery performed?")
            - Medicine or pharmaceuticals ("What is aspirin used for?")
            - Direct patient care questions ("When should I see a doctor?")
            
            Be very strict - if there's any doubt, reply "NOT_RELEVANT".
            
            Response (only "RELEVANT" or "NOT_RELEVANT"):
            """
            
            topic_response = self.text_model.generate_content(topic_check_prompt)
            
            if "NOT_RELEVANT" in topic_response.text:
                return "I'm a specialized medical AI assistant focused on radiology and healthcare topics. I can help you with:\n\n• Medical symptoms and conditions\n• Radiology and medical imaging questions\n• Treatment options and medications\n• When to seek medical care\n• Health and wellness guidance\n\nHow can I assist you with a medical or health-related question today?"
            
            # Build context from history
            context = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    context += f"{msg['sender']}: {msg['message']}\n"
            
            prompt = f"""
            You are a STRICT medical AI assistant for a radiology platform. You MUST ONLY respond to questions about direct patient care, symptoms, medical conditions, treatments, and radiology.

            STRICT RULES - REFUSE to discuss:
            - General technology topics (AI, machine learning, deep learning, programming)
            - Educational topics not directly related to patient symptoms or treatment
            - Science topics unless directly about medical conditions
            - Any non-medical topics whatsoever

            ONLY DISCUSS:
            - Patient symptoms and medical conditions
            - Medical treatments and medications
            - Radiology and medical imaging for patient care
            - When to seek medical care
            - Health and wellness advice

            If the user asks about non-medical topics, politely redirect them to medical questions.

            Previous conversation:
            {context}
            
            User: {user_message}
            
            Response Guidelines:
            1. Be empathetic and clear about medical topics only
            2. Use simple language for medical information
            3. Include medical disclaimers for health advice
            4. Encourage professional medical consultation
            5. REFUSE non-medical discussions politely
            6. Never provide emergency medical advice
            
            Assistant:
            """
            
            response = self.text_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or contact support."
    
    async def chat_response_with_scan_context(
        self,
        user_message: str,
        scan,  # RadiologyScan model instance
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate chatbot response with specific scan context and analysis results.
        
        Args:
            user_message: User's message
            scan: RadiologyScan model instance with analysis results
            conversation_history: Previous messages for context
            
        Returns:
            AI response text with scan-specific insights
        """
        try:
            import json
            
            # Build scan context information
            scan_context = {
                "scan_id": scan.id,
                "modality": scan.modality.value,
                "upload_date": str(scan.upload_date),
                "description": scan.description or "No description provided",
                "ai_analyzed": scan.ai_analyzed
            }
            
            # Add AI analysis results if available
            if scan.ai_analyzed:
                scan_context.update({
                    "disease_classification": scan.disease_classification or "Unknown",
                    "confidence_score": scan.confidence_score or 0.0,
                    "risk_level": scan.risk_level.value if scan.risk_level else "Unknown",
                    "ai_explanation": scan.ai_explanation or "No explanation available"
                })
                
                # Parse abnormalities if available
                if scan.detected_abnormalities:
                    try:
                        abnormalities = json.loads(scan.detected_abnormalities)
                        scan_context["abnormalities"] = abnormalities
                    except:
                        scan_context["abnormalities"] = []
                else:
                    scan_context["abnormalities"] = []
            
            # Build context from conversation history
            history_context = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    history_context += f"{msg['sender']}: {msg['message']}\n"
            
            prompt = f"""
            You are a SPECIALIZED medical AI assistant for a radiology platform with access to specific scan analysis results.

            SCAN CONTEXT:
            - Scan ID: {scan_context['scan_id']}
            - Modality: {scan_context['modality']} 
            - Date: {scan_context['upload_date']}
            - Description: {scan_context['description']}
            - AI Analyzed: {scan_context['ai_analyzed']}
            
            {f'''
            AI ANALYSIS RESULTS:
            - Disease Classification: {scan_context.get('disease_classification', 'Not available')}
            - Confidence Score: {scan_context.get('confidence_score', 'Not available')}
            - Risk Level: {scan_context.get('risk_level', 'Not available')}
            - Detected Abnormalities: {scan_context.get('abnormalities', 'None detected')}
            - AI Explanation: {scan_context.get('ai_explanation', 'Not available')}
            ''' if scan.ai_analyzed else 'AI ANALYSIS: This scan has not been analyzed by AI yet.'}

            CONVERSATION HISTORY:
            {history_context}

            USER QUESTION: {user_message}

            INSTRUCTIONS:
            1. Use the scan analysis results to provide context-aware responses
            2. Reference specific findings from this scan when relevant
            3. Explain medical terms in simple language
            4. Provide insights about the scan findings if asked
            5. Always include appropriate medical disclaimers
            6. If the scan hasn't been analyzed, suggest getting it analyzed first
            7. Focus only on medical/radiology topics related to this scan
            8. Encourage consultation with healthcare providers for diagnosis and treatment

            RESPONSE GUIDELINES:
            - Be specific about findings from THIS scan
            - Reference the scan's modality, date, and results
            - Provide educational information about detected conditions
            - Suggest next steps or follow-up if appropriate
            - Include disclaimers about not replacing professional medical advice

            Respond in a helpful, clear, and medical-appropriate manner:
            """
            
            response = self.text_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I apologize, but I encountered an error analyzing your scan context: {str(e)}. Please try again or contact support."

    async def suggest_medicines(
        self,
        disease_classification: str,
        symptoms: str,
        patient_age: Optional[int] = None,
        scan_findings: Optional[Dict] = None
    ) -> Dict:
        """
        Suggest medicines based on disease classification with Bangladesh perspective.
        
        Args:
            disease_classification: Diagnosed condition
            symptoms: Patient symptoms
            patient_age: Optional patient age
            scan_findings: Optional scan analysis results
            
        Returns:
            Dict with medicine suggestions
        """
        try:
            scan_context = ""
            if scan_findings:
                scan_context = f"""
            
            Scan Findings:
            - Abnormalities detected: {scan_findings.get('abnormalities', [])}
            - Risk Level: {scan_findings.get('risk_level', 'Unknown')}
            - AI Confidence: {scan_findings.get('confidence', 'Unknown')}%
            - Additional findings: {scan_findings.get('explanation', '')}
            """
            
            prompt = f"""
            As a medical AI assistant with expertise in Bangladesh healthcare system, suggest commonly prescribed medicines for:
            
            Condition: {disease_classification}
            Symptoms: {symptoms}
            {f"Patient Age: {patient_age}" if patient_age else ""}
            {scan_context}
            
            IMPORTANT: Focus on medicines commonly available in Bangladesh, including:
            - Generic medicines available in Bangladesh pharmacies
            - Local pharmaceutical brands (e.g., Square, Beximco, Incepta, ACI, etc.)
            - Consider Bangladesh's tropical climate and common health conditions
            - Include traditional/herbal alternatives where appropriate
            
            Provide suggestions in JSON format:
            {{
                "medicines": [
                    {{
                        "name": "medicine name (include generic and Bangladesh brand if available)",
                        "generic_name": "active ingredient",
                        "bangladesh_brands": ["Brand1", "Brand2"],
                        "purpose": "what it treats",
                        "general_usage": "typical usage information",
                        "precautions": "important precautions",
                        "availability": "commonly available/prescription required/OTC",
                        "approximate_cost": "price range in Bangladesh Taka (BDT)"
                    }}
                ],
                "lifestyle_recommendations": [
                    "Bangladesh-specific lifestyle and dietary recommendations"
                ],
                "follow_up": "Recommended follow-up timeline",
                "disclaimer": "Important medical disclaimer emphasizing consultation with local healthcare provider"
            }}
            
            CRITICAL: 
            - Include strong disclaimer about consulting healthcare provider
            - Mention consultation with registered doctors in Bangladesh
            - Do NOT provide specific dosages
            - Consider Bangladesh's healthcare infrastructure and accessibility
            """
            
            response = self.text_model.generate_content(prompt)
            result = self._parse_ai_response(response.text)
            
            return result
            
        except Exception as e:
            return {
                "medicines": [],
                "lifestyle_recommendations": [],
                "follow_up": "Consult with a healthcare provider immediately",
                "disclaimer": "Medicine suggestion unavailable. Please consult a registered healthcare provider in Bangladesh.",
                "error": str(e)
            }
    
    async def generate_health_summary(
        self,
        patient_data: Dict,
        recent_reports: List[Dict]
    ) -> str:
        """
        Generate comprehensive health summary.
        
        Args:
            patient_data: Patient information
            recent_reports: List of recent medical reports
            
        Returns:
            Health summary text
        """
        try:
            prompt = f"""
            Generate a concise health summary for:
            
            Patient Data:
            {json.dumps(patient_data, indent=2)}
            
            Recent Reports:
            {json.dumps(recent_reports, indent=2)}
            
            Provide:
            1. Current health status overview
            2. Key findings from recent scans
            3. Risk factors identified
            4. Recommended follow-up actions
            5. Overall health trajectory
            
            Keep it clear and patient-friendly while being medically accurate.
            """
            
            response = self.text_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Health summary generation failed: {str(e)}"
    
    async def assess_risk_profile(
        self,
        findings: List[str],
        medical_history: Optional[str] = None
    ) -> Dict:
        """
        Assess patient risk profile.
        
        Args:
            findings: List of medical findings
            medical_history: Patient medical history
            
        Returns:
            Risk assessment dict
        """
        try:
            prompt = f"""
            Assess patient risk profile based on:
            
            Findings: {json.dumps(findings)}
            {f"Medical History: {medical_history}" if medical_history else ""}
            
            Provide risk assessment in JSON:
            {{
                "overall_risk": "LOW/MEDIUM/HIGH",
                "risk_factors": ["identified factors"],
                "priority_level": "routine/urgent/immediate",
                "recommendations": ["recommended actions"],
                "explanation": "detailed risk explanation"
            }}
            """
            
            response = self.text_model.generate_content(prompt)
            result = self._parse_ai_response(response.text)
            
            return result
            
        except Exception as e:
            return {
                "overall_risk": "MEDIUM",
                "risk_factors": [],
                "explanation": f"Risk assessment error: {str(e)}"
            }
    
    async def generate_risk_profile(
        self,
        patient_info: Dict,
        scan_findings: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive risk profile based on multiple radiology scans.
        
        Args:
            patient_info: Patient information including age, name, etc.
            scan_findings: List of analyzed scan results
            
        Returns:
            Dict containing risk assessment and recommendations
        """
        try:
            # Prepare scan summary for AI analysis
            scan_summary = []
            for finding in scan_findings:
                scan_summary.append({
                    "modality": finding.get("modality"),
                    "date": finding.get("date"),
                    "classification": finding.get("disease_classification"),
                    "risk_level": finding.get("risk_level"),
                    "confidence": finding.get("confidence_score"),
                    "abnormalities_count": len(finding.get("abnormalities", [])),
                    "key_findings": finding.get("explanation", "")
                })
            
            prompt = f"""
            As a medical AI specialist, analyze the following patient's radiology scan history and provide a comprehensive risk profile:
            
            Patient Information:
            {json.dumps(patient_info, indent=2)}
            
            Scan History Summary:
            {json.dumps(scan_summary, indent=2)}
            
            Detailed Scan Findings:
            {json.dumps(scan_findings, indent=2)}
            
            Provide a comprehensive risk assessment in JSON format:
            {{
                "overall_risk_assessment": {{
                    "primary_concerns": ["list of main health concerns"],
                    "risk_factors": ["identified risk factors"],
                    "progressive_changes": "analysis of changes over time if multiple scans",
                    "critical_findings": ["any critical findings requiring immediate attention"]
                }},
                "health_outlook": {{
                    "short_term_prognosis": "1-6 month outlook",
                    "long_term_prognosis": "6+ month outlook",
                    "preventive_measures": ["recommended preventive actions"],
                    "lifestyle_modifications": ["suggested lifestyle changes"]
                }},
                "monitoring_recommendations": {{
                    "follow_up_frequency": "recommended scan frequency",
                    "specific_tests": ["additional tests if needed"],
                    "warning_signs": ["symptoms to watch for"],
                    "emergency_indicators": ["signs requiring immediate medical attention"]
                }},
                "bangladesh_context": {{
                    "environmental_factors": ["relevant environmental health factors in Bangladesh"],
                    "seasonal_considerations": ["monsoon, humidity, pollution effects"],
                    "local_healthcare_recommendations": ["specific advice for Bangladesh healthcare system"],
                    "dietary_considerations": ["Bangladesh diet-specific recommendations"]
                }},
                "confidence_assessment": {{
                    "analysis_reliability": "percentage",
                    "data_completeness": "assessment of available data",
                    "recommendation_strength": "strength of recommendations"
                }},
                "summary": "Brief overall summary of patient's radiological risk profile"
            }}
            
            Focus on:
            - Pattern recognition across multiple scans
            - Progressive disease indicators
            - Risk stratification
            - Bangladesh-specific health considerations (climate, pollution, common diseases)
            - Actionable recommendations
            
            IMPORTANT: Provide realistic assessments and emphasize the need for professional medical consultation.
            """
            
            response = self.text_model.generate_content(prompt)
            result = self._parse_ai_response(response.text)
            
            return result
            
        except Exception as e:
            return {
                "overall_risk_assessment": {
                    "primary_concerns": ["Analysis unavailable"],
                    "risk_factors": [],
                    "progressive_changes": "Unable to analyze",
                    "critical_findings": []
                },
                "health_outlook": {
                    "short_term_prognosis": "Consult healthcare provider for assessment",
                    "long_term_prognosis": "Professional evaluation required",
                    "preventive_measures": ["Regular medical check-ups"],
                    "lifestyle_modifications": ["Maintain healthy lifestyle"]
                },
                "monitoring_recommendations": {
                    "follow_up_frequency": "As advised by healthcare provider",
                    "specific_tests": [],
                    "warning_signs": ["Any new or worsening symptoms"],
                    "emergency_indicators": ["Severe symptoms requiring immediate care"]
                },
                "bangladesh_context": {
                    "environmental_factors": ["Monitor air quality", "Stay hydrated"],
                    "seasonal_considerations": ["Be cautious during monsoon season"],
                    "local_healthcare_recommendations": ["Consult registered physician in Bangladesh"],
                    "dietary_considerations": ["Maintain balanced diet with local foods"]
                },
                "confidence_assessment": {
                    "analysis_reliability": "0%",
                    "data_completeness": "Insufficient",
                    "recommendation_strength": "Weak - professional consultation required"
                },
                "summary": "Risk profile analysis unavailable. Please consult with a healthcare professional.",
                "error": str(e)
            }

    def _parse_ai_response(self, response_text: str) -> Dict:
        """
        Parse AI response text to extract JSON.
        
        Args:
            response_text: Raw AI response
            
        Returns:
            Parsed dictionary
        """
        try:
            # Try to find JSON in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If no JSON found, return text as-is
            return {"response": response_text}
            
        except json.JSONDecodeError:
            return {"response": response_text}


# Create global instance
gemini_service = GeminiAIService()
