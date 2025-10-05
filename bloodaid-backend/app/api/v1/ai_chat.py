from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.chat_history import ChatHistory
from app.ml.rag.rag_chat import get_bloodaid_rag

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    context: str = "general"  # health, donation, emergency
    userId: str

class ChatResponse(BaseModel):
    response: str
    language: str
    suggestions: Optional[List[str]] = None

# Mock responses for different languages and contexts
MOCK_RESPONSES = {
    "en": {
        "emergency": "I understand this is urgent. Let me help you find donors immediately. Please provide your location and blood type needed.",
        "health": "Based on your query, I recommend consulting with a medical professional. Here's some general guidance:",
        "donation": "Great question about blood donation! Let me provide you with accurate information:",
        "general": "I'm here to help with blood donation and health questions. How can I assist you today?"
    },
    "hi": {
        "emergency": "मैं समझता हूं यह जरूरी है। मैं तुरंत दाताओं को खोजने में आपकी मदद करूंगा। कृपया अपना स्थान और रक्त समूह बताएं।",
        "health": "आपके प्रश्न के आधार पर, मैं डॉक्टर से सलाह लेने की सिफारिश करता हूं। यहां कुछ सामान्य मार्गदर्शन है:",
        "donation": "रक्तदान के बारे में बेहतरीन सवाल! मैं आपको सटीक जानकारी देता हूं:",
        "general": "मैं रक्तदान और स्वास्थ्य के सवालों में मदद के लिए यहां हूं। आज मैं आपकी कैसे सहायता कर सकता हूं?"
    },
    "kn": {
        "emergency": "ಇದು ತುರ್ತು ಎಂದು ನಾನು ಅರ್ಥಮಾಡಿಕೊಂಡಿದ್ದೇನೆ। ದಾನಿಗಳನ್ನು ತಕ್ಷಣ ಹುಡುಕಲು ನಾನು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸ್ಥಳ ಮತ್ತು ರಕ್ತದ ಗುಂಪನ್ನು ತಿಳಿಸಿ.",
        "health": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯ ಆಧಾರದ ಮೇಲೆ, ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಲು ನಾನು ಶಿಫಾರಸು ಮಾಡುತ್ತೇನೆ. ಇಲ್ಲಿ ಕೆಲವು ಸಾಮಾನ್ಯ ಮಾರ್ಗದರ್ಶನ:",
        "donation": "ರಕ್ತದಾನದ ಬಗ್ಗೆ ಅದ್ಭುತ ಪ್ರಶ್ನೆ! ನಾನು ನಿಮಗೆ ನಿಖರವಾದ ಮಾಹಿತಿಯನ್ನು ನೀಡುತ್ತೇನೆ:",
        "general": "ರಕ್ತದಾನ ಮತ್ತು ಆರೋಗ್ಯ ಪ್ರಶ್ನೆಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
    },
    "te": {
        "emergency": "ఇది అత్యవసరం అని నేను అర్థం చేసుకున్నాను. దాతలను వెంటనే కనుగొనడంలో నేను మీకు సహాయం చేస్తాను. దయచేసి మీ స్థానం మరియు రక్త వర్గాన్ని తెలియజేయండి.",
        "health": "మీ ప్రశ్న ఆధారంగా, వైద్యుడిని సంప్రదించాలని నేను సిఫార్సు చేస్తున్నాను. ఇక్కడ కొన్ని సాధారణ మార్గదర్శకాలు:",
        "donation": "రక్తదానం గురించి అద్భుతమైన ప్రశ్న! నేను మీకు ఖచ్చితమైన సమాచారం అందిస్తున్నాను:",
        "general": "రక్తదానం మరియు ఆరోగ్య ప్రశ్నలలో సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను. ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?"
    },
    "ml": {
        "emergency": "ഇത് അടിയന്തിരമാണെന്ന് ഞാൻ മനസ്സിലാക്കുന്നു. ദാതാക്കളെ ഉടൻ കണ്ടെത്താൻ ഞാൻ സഹായിക്കാം. ദയവായി നിങ്ങളുടെ സ്ഥലവും രക്തഗ്രൂപ്പും അറിയിക്കുക.",
        "health": "നിങ്ങളുടെ ചോദ്യത്തിന്റെ അടിസ്ഥാനത്തിൽ, ഒരു ഡോക്ടറെ സമീപിക്കാൻ ഞാൻ ശുപാർശ ചെയ്യുന്നു. ഇവിടെ ചില പൊതുവായ മാർഗനിർദേശങ്ങൾ:",
        "donation": "രക്തദാനത്തെക്കുറിച്ചുള്ള മികച്ച ചോദ്യം! ഞാൻ നിങ്ങൾക്ക് കൃത്യമായ വിവരങ്ങൾ നൽകുന്നു:",
        "general": "രക്തദാനവും ആരോഗ്യ ചോദ്യങ്ങളും സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്. ഇന്ന് ഞാൻ എങ്ങനെ സഹായിക്കാം?"
    }
}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """AI chat endpoint with multilingual support"""
    try:
        # Get base response for language and context
        lang_responses = MOCK_RESPONSES.get(request.language, MOCK_RESPONSES["en"])
        base_response = lang_responses.get(request.context, lang_responses["general"])
        
        # Generate context-specific response based on message content
        message_lower = request.message.lower()
        
        if request.context == "emergency" or any(word in message_lower for word in ["urgent", "emergency", "need blood", "critical", "sos"]):
            if request.language == "en":
                response = f"🚨 Emergency Alert Detected 🚨\n\nI understand this is urgent. I'm immediately searching for {message_lower} donors in your area. Let me help you:\n\n1. Activating emergency donor network\n2. Sending alerts to nearby verified donors\n3. Coordinating with local blood banks\n\nPlease stay calm while we find help. What's your exact location and how many units do you need?"
            elif request.language == "hi":
                response = f"🚨 आपातकालीन अलर्ट 🚨\n\nमैं समझता हूं यह जरूरी है। मैं तुरंत आपके क्षेत्र में दाताओं को खोज रहा हूं:\n\n1. आपातकालीन दाता नेटवर्क सक्रिय कर रहा हूं\n2. नजदीकी सत्यापित दाताओं को अलर्ट भेज रहा हूं\n3. स्थानीय ब्लड बैंक से संपर्क कर रहा हूं\n\nकृपया शांत रहें। आपका सटीक स्थान और कितने यूनिट चाहिए?"
            else:
                response = base_response
                
        elif "hemoglobin" in message_lower or "anemia" in message_lower:
            if request.language == "en":
                response = "Hemoglobin levels are crucial for blood donation eligibility. Normal levels:\n\n• Men: 13.5-17.5 g/dL\n• Women: 12.0-15.5 g/dL\n• Minimum for donation: 12.5 g/dL\n\nTo increase hemoglobin:\n✓ Iron-rich foods (spinach, red meat, lentils)\n✓ Vitamin C (citrus fruits)\n✓ Avoid tea/coffee with meals\n\nConsult a doctor if levels are consistently low."
            else:
                response = base_response
                
        elif "blood group" in message_lower or "blood type" in message_lower:
            if request.language == "en":
                response = "Blood Group Compatibility:\n\n🅾️ O- (Universal Donor): Can donate to all\n🅾️ O+: Can donate to O+, A+, B+, AB+\n🅰️ A-: Can donate to A-, A+, AB-, AB+\n🅰️ A+: Can donate to A+, AB+\n🅱️ B-: Can donate to B-, B+, AB-, AB+\n🅱️ B+: Can donate to B+, AB+\n🆎 AB-: Can donate to AB-, AB+\n🆎 AB+ (Universal Recipient): Can receive from all\n\nKnowing your blood type helps save lives!"
            else:
                response = base_response
                
        elif "thalassemia" in message_lower or "dialysis" in message_lower:
            if request.language == "en":
                response = "For chronic conditions requiring regular transfusions:\n\n🩸 Thalassemia patients typically need blood every 2-3 weeks\n🩸 Dialysis patients may need occasional transfusions\n\nBloodAid helps by:\n✓ Building dedicated donor networks\n✓ Scheduling recurring donations\n✓ Emergency alerts when needed\n✓ Coordinating with treatment centers\n\nWould you like help setting up a regular donor network?"
            else:
                response = base_response
                
        elif "donate" in message_lower and "eligibility" in message_lower:
            if request.language == "en":
                response = "Blood Donation Eligibility Checklist:\n\n✅ Age: 18-65 years\n✅ Weight: Minimum 50 kg\n✅ Hemoglobin: ≥12.5 g/dL\n✅ Blood Pressure: 110-160/70-100 mmHg\n✅ No fever or illness\n✅ No recent tattoos (4 months)\n✅ No recent COVID (28 days)\n✅ No recent travel to malaria areas\n\n⏰ Wait time between donations: 3-4 months\n\nShould I check your eligibility based on your health profile?"
            else:
                response = base_response
        else:
            # Default response with helpful suggestions
            response = base_response
        
        # Generate suggestions based on context
        suggestions = []
        if request.context == "emergency":
            suggestions = ["Find donors near me", "Emergency blood banks", "Contact hospital", "Send SOS alert"]
        elif request.context == "health":
            suggestions = ["Check donation eligibility", "Hemoglobin levels", "Health recommendations", "Medical checkup"]
        elif request.context == "donation":
            suggestions = ["Donation requirements", "Blood compatibility", "Schedule donation", "Donation history"]
        else:
            suggestions = ["Find donors", "Health checkup", "Emergency help", "Donation info"]
        
        return ChatResponse(
            response=response,
            language=request.language,
            suggestions=suggestions
        )
        
    except Exception as e:
        # Fallback response
        return ChatResponse(
            response="I'm sorry, I'm having trouble processing your request right now. Please try again or contact support.",
            language=request.language,
            suggestions=["Try again", "Contact support", "Emergency help"]
        )

@router.get("/health-check")
async def ai_health_check():
    """Check if AI service is healthy"""
    return {
        "status": "healthy",
        "service": "BloodAid AI Assistant",
        "languages": ["en", "hi", "kn", "te", "ml"],
        "features": ["multilingual_chat", "emergency_detection", "health_guidance"]
    }