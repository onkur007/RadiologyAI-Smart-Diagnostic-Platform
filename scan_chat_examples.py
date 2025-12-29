#!/usr/bin/env python3
"""
Example usage scenarios for the Scan-Specific AI Chat API.
This demonstrates real-world use cases and integration patterns.
"""

class ScanChatExamples:
    """Examples of using the scan-specific chat API"""
    
    def __init__(self, base_url="http://localhost:8000", auth_token=None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {"Authorization": f"Bearer {auth_token}"}
    
    def example_1_initial_scan_consultation(self):
        """
        Example 1: Patient asks about their newly uploaded scan
        """
        print("Example 1: Initial Scan Consultation")
        print("-" * 40)
        
        # Patient just uploaded a chest X-ray and wants to know about findings
        request_data = {
            "message": "I just uploaded my chest X-ray. Can you tell me what the findings mean?",
            "scan_id": 1,
            "session_id": None  # New conversation
        }
        
        print(f"Request: {request_data}")
        print("\nExpected AI Response:")
        print("""
        Based on your chest X-ray from December 29, 2025, our AI analysis 
        detected an opacity in the right lower lobe with 85% confidence. 
        This finding suggests pneumonia, which is an infection of the lung tissue.
        
        Key findings from your scan:
        - Modality: Chest X-ray
        - Main finding: Right lower lobe opacity
        - AI confidence: 85%
        - Risk level: Medium
        - Disease classification: Pneumonia
        
        What this means:
        - An opacity appears as a white/cloudy area on X-ray
        - Indicates inflammation or infection in lung tissue
        - Requires prompt medical attention
        
        Next steps I recommend:
        1. Contact your healthcare provider immediately
        2. Discuss antibiotic treatment options
        3. Schedule follow-up imaging if recommended
        
        ⚠️ This is AI analysis for educational purposes. Please consult 
        your healthcare provider for proper diagnosis and treatment.
        """)
    
    def example_2_follow_up_questions(self):
        """
        Example 2: Patient asks follow-up questions in the same session
        """
        print("\nExample 2: Follow-up Questions")
        print("-" * 40)
        
        # Patient continues the conversation from Example 1
        followup_requests = [
            {
                "message": "How serious is pneumonia? Should I be worried?",
                "scan_id": 1,
                "session_id": 1  # Continue previous session
            },
            {
                "message": "What symptoms should I watch out for?",
                "scan_id": 1,
                "session_id": 1
            },
            {
                "message": "How long will recovery take?",
                "scan_id": 1,
                "session_id": 1
            }
        ]
        
        for i, request in enumerate(followup_requests, 1):
            print(f"\nRequest {i}: {request['message']}")
            print("Expected AI Response: Personalized response based on specific")
            print("scan findings, with reassurance and medical guidance.")
    
    def example_3_doctor_consultation(self):
        """
        Example 3: Doctor reviewing patient scan with AI assistance
        """
        print("\nExample 3: Doctor Consultation")
        print("-" * 40)
        
        # Doctor wants AI insights for patient consultation
        doctor_request = {
            "message": "What are the key points I should discuss with this patient about their scan findings?",
            "scan_id": 1,
            "session_id": None
        }
        
        print(f"Doctor Request: {doctor_request}")
        print("\nExpected AI Response for Doctor:")
        print("""
        Key discussion points for patient consultation:
        
        Scan Summary:
        - Chest X-ray showing right lower lobe opacity
        - AI confidence: 85% for pneumonia diagnosis
        - Medium risk classification
        
        Patient Communication Points:
        1. Explain what opacity means in simple terms
        2. Discuss pneumonia as treatable condition
        3. Emphasize importance of prompt treatment
        4. Address patient concerns about severity
        
        Treatment Discussion:
        - Antibiotic therapy recommendations
        - Expected recovery timeline
        - Follow-up imaging schedule
        - Warning signs to watch for
        
        Documentation:
        - Confirm AI findings with clinical assessment
        - Document treatment plan
        - Schedule appropriate follow-up
        """)
    
    def example_4_comparative_analysis(self):
        """
        Example 4: Comparing multiple scans for the same patient
        """
        print("\nExample 4: Comparative Analysis")
        print("-" * 40)
        
        # Patient has multiple scans and wants to compare
        comparison_requests = [
            {
                "message": "How does this scan compare to my previous chest X-ray from last month?",
                "scan_id": 2,  # Latest scan
                "session_id": None
            },
            {
                "message": "Show me the differences between scan ID 1 and scan ID 2",
                "scan_id": 2,
                "session_id": None
            }
        ]
        
        for request in comparison_requests:
            print(f"Request: {request['message']}")
            print("AI would analyze the specific scan and provide context")
            print("about changes, improvements, or new findings.\n")
    
    def example_5_educational_queries(self):
        """
        Example 5: Educational questions about specific findings
        """
        print("\nExample 5: Educational Queries")
        print("-" * 40)
        
        educational_questions = [
            "What causes opacity in lungs?",
            "How accurate is AI in detecting pneumonia?",
            "What does confidence score of 85% mean?",
            "Should I get a second opinion?",
            "What other tests might I need?"
        ]
        
        for question in educational_questions:
            print(f"Question: {question}")
            print("AI provides personalized education based on")
            print("the specific scan findings and context.\n")
    
    def example_6_integration_patterns(self):
        """
        Example 6: Common integration patterns for frontend
        """
        print("\nExample 6: Frontend Integration Patterns")
        print("-" * 40)
        
        integration_code = '''
        // React component example
        const ScanChatInterface = ({ scanId, userId }) => {
          const [messages, setMessages] = useState([]);
          const [currentMessage, setCurrentMessage] = useState('');
          const [sessionId, setSessionId] = useState(null);
          
          const sendMessage = async () => {
            try {
              const response = await fetch('/ai/chat/scan', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                  message: currentMessage,
                  scan_id: scanId,
                  session_id: sessionId
                })
              });
              
              const data = await response.json();
              setSessionId(data.session_id);
              setMessages(prev => [...prev, data]);
              setCurrentMessage('');
              
            } catch (error) {
              console.error('Chat failed:', error);
            }
          };
          
          return (
            <div className="scan-chat-interface">
              <div className="scan-context">
                Discussing Scan #{scanId}
              </div>
              <div className="messages">
                {messages.map(msg => (
                  <div key={msg.id} className={msg.sender}>
                    {msg.message}
                  </div>
                ))}
              </div>
              <input 
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder="Ask about your scan..."
              />
              <button onClick={sendMessage}>Send</button>
            </div>
          );
        };
        '''
        
        print("Frontend Integration Example:")
        print(integration_code)

def main():
    """Run all examples"""
    print("Scan-Specific AI Chat API - Usage Examples")
    print("=" * 50)
    
    examples = ScanChatExamples()
    
    examples.example_1_initial_scan_consultation()
    examples.example_2_follow_up_questions()
    examples.example_3_doctor_consultation()
    examples.example_4_comparative_analysis()
    examples.example_5_educational_queries()
    examples.example_6_integration_patterns()
    
    print("\n" + "=" * 50)
    print("Key Benefits of Scan-Specific Chat:")
    print("✅ Context-aware responses based on actual scan findings")
    print("✅ Personalized medical education")
    print("✅ Improved patient understanding")
    print("✅ Better doctor-patient communication")
    print("✅ Maintained conversation history")
    print("✅ Secure access control")
    
    print("\nBest Practices:")
    print("🔒 Always validate scan ownership")
    print("⚕️ Include medical disclaimers")
    print("📱 Design for mobile-first UI")
    print("💬 Provide suggested questions")
    print("🔄 Enable session continuity")
    print("📊 Track usage analytics")

if __name__ == "__main__":
    main()
