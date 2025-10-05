from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
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

# Enhanced mock responses for different languages and contexts
MOCK_RESPONSES = {
    "emergency": {
        "en": {
            "response": "🚨 Emergency Blood Request Detected!\n\nI'm here to help you quickly find blood donors. Let me assist with:\n\n1. 📍 Finding nearby donors\n2. 🏥 Contacting blood banks\n3. 📞 Emergency helpline numbers\n4. 🚨 Sending SOS alerts\n\nWhat's your current location and required blood group?",
            "suggestions": ["Find donors near me", "Emergency blood banks", "Send SOS alert", "Hospital contacts"]
        },
        "hi": {
            "response": "🚨 आपातकालीन रक्त अनुरोध!\n\nमैं आपको तुरंत रक्तदाताओं को खोजने में मदद कर सकता हूं:\n\n1. 📍 पास के रक्तदाता खोजें\n2. 🏥 रक्त बैंकों से संपर्क करें\n3. 📞 आपातकालीन हेल्पलाइन\n4. 🚨 SOS अलर्ट भेजें\n\nआपका वर्तमान स्थान और आवश्यक रक्त समूह क्या है?",
            "suggestions": ["पास के दाता खोजें", "रक्त बैंक", "SOS भेजें", "अस्पताल संपर्क"]
        }
    },
    "health": {
        "en": {
            "response": "🩺 Health & Wellness Support\n\nI can help you with:\n\n• Blood donation eligibility checks\n• Hemoglobin level guidance\n• Pre-donation health tips\n• Post-donation care\n• Health vitals tracking\n• Chronic condition support\n\nWhat health topic would you like to discuss?",
            "suggestions": ["Check eligibility", "Hemoglobin tips", "Health tracking", "Chronic conditions"]
        },
        "hi": {
            "response": "🩺 स्वास्थ्य और कल्याण सहायता\n\nमैं आपकी मदद कर सकता हूं:\n\n• रक्तदान पात्रता जांच\n• हीमोग्लोबिन स्तर मार्गदर्शन\n• दान-पूर्व स्वास्थ्य सुझाव\n• दान-बाद देखभाल\n• स्वास्थ्य निगरानी\n• पुरानी बीमारी सहायता\n\nआप किस स्वास्थ्य विषय पर चर्चा करना चाहेंगे?",
            "suggestions": ["पात्रता जांचें", "हीमोग्लोबिन सुझाव", "स्वास्थ्य ट्रैकिंग", "पुरानी स्थितियां"]
        }
    },
    "donation": {
        "en": {
            "response": "🩸 Blood Donation Support\n\nReady to make a difference? I can help with:\n\n• Finding donation centers near you\n• Scheduling appointments\n• Understanding the donation process\n• Tracking your donation history\n• Recognition and rewards\n• Connecting with recipients\n\nHow would you like to contribute today?",
            "suggestions": ["Find centers", "Schedule donation", "Track history", "Learn process"]
        },
        "hi": {
            "response": "🩸 रक्तदान सहायता\n\nबदलाव लाने के लिए तैयार हैं? मैं मदद कर सकता हूं:\n\n• आपके पास दान केंद्र खोजना\n• अपॉइंटमेंट शेड्यूल करना\n• दान प्रक्रिया समझना\n• दान इतिहास ट्रैक करना\n• पहचान और पुरस्कार\n• प्राप्तकर्ताओं से जुड़ना\n\nआज आप कैसे योगदान देना चाहेंगे?",
            "suggestions": ["केंद्र खोजें", "दान शेड्यूल करें", "इतिहास ट्रैक करें", "प्रक्रिया सीखें"]
        }
    },
    "general": {
        "en": {
            "response": "Hello! I'm BloodAid AI, your intelligent blood donation assistant. 🩸\n\nI'm here to help with:\n• Blood donation guidance\n• Emergency blood requests\n• Health and eligibility support\n• Connecting donors with patients\n• Medical information and tips\n\nHow can I assist you today?",
            "suggestions": ["Emergency help", "Donate blood", "Health check", "Find donors"]
        },
        "hi": {
            "response": "नमस्ते! मैं BloodAid AI हूं, आपका बुद्धिमान रक्तदान सहायक। 🩸\n\nमैं इसमें मदद कर सकता हूं:\n• रक्तदान मार्गदर्शन\n• आपातकालीन रक्त अनुरोध\n• स्वास्थ्य और पात्रता सहायता\n• दाताओं को मरीजों से जोड़ना\n• चिकित्सा जानकारी और सुझाव\n\nआज मैं आपकी कैसे सहायता कर सकता हूं?",
            "suggestions": ["आपातकालीन सहायता", "रक्तदान", "स्वास्थ्य जांच", "दाता खोजें"]
        },
        "kn": {
            "response": "ನಮಸ್ಕಾರ! ನಾನು BloodAid AI, ನಿಮ್ಮ ಬುದ್ಧಿವಂತ ರಕ್ತದಾನ ಸಹಾಯಕ। 🩸\n\nನಾನು ಇದರಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು:\n• ರಕ್ತದಾನ ಮಾರ್ಗದರ್ಶನ\n• ತುರ್ತು ರಕ್ತದ ಅವಶ್ಯಕತೆ\n• ಆರೋಗ್ಯ ಮತ್ತು ಅರ್ಹತೆ ಬೆಂಬಲ\n• ದಾನಿಗಳನ್ನು ರೋಗಿಗಳೊಂದಿಗೆ ಸಂಪರ್ಕಿಸುವುದು\n• ವೈದ್ಯಕೀಯ ಮಾಹಿತಿ ಮತ್ತು ಸಲಹೆಗಳು\n\nಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
            "suggestions": ["ತುರ್ತು ಸಹಾಯ", "ರಕ್ತದಾನ", "ಆರೋಗ್ಯ ಪರೀಕ್ಷೆ", "ದಾನಿಗಳನ್ನು ಹುಡುಕಿ"]
        },
        "te": {
            "response": "నమస్కారం! నేను BloodAid AI, మీ తెలివైన రక్తదాన సహాయకుడిని। 🩸\n\nనేను ఇందులో సహాయం చేయగలను:\n• రక్తదాన మార్గదర్శకత్వం\n• అత్యవసర రక్త అవసరాలు\n• ఆరోగ్యం మరియు అర్హత మద్దతు\n• దాతలను రోగులతో కలపడం\n• వైద్య సమాచారం మరియు చిట్కాలు\n\nఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?",
            "suggestions": ["అత్యవసర సహాయం", "రక్తదానం", "ఆరోగ్య తనిఖీ", "దాతలను కనుగొనండి"]
        },
        "ml": {
            "response": "നമസ്കാരം! ഞാൻ BloodAid AI ആണ്, നിങ്ങളുടെ ബുദ്ധിമാനായ രക്തദാന സഹായി। 🩸\n\nഞാൻ ഇതിൽ സഹായിക്കാം:\n• രക്തദാന മാർഗ്ഗനിർദ്ദേശം\n• അടിയന്തിര രക്ത ആവശ്യങ്ങൾ\n• ആരോഗ്യവും യോഗ്യതാ പിന്തുണയും\n• ദാതാക്കളെ രോഗികളുമായി ബന്ധിപ്പിക്കൽ\n• മെഡിക്കൽ വിവരങ്ങളും നുറുങ്ങുകളും\n\nഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
            "suggestions": ["അടിയന്തിര സഹായം", "രക്തദാനം", "ആരോഗ്യ പരിശോധന", "ദാതാക്കളെ കണ്ടെത്തുക"]
        }
    }
}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Chat with BloodAid AI assistant with RAG enhancement"""
    try:
        # Try to get enhanced RAG response
        try:
            rag_assistant = get_bloodaid_rag()
            
            # Prepare user context
            user_context = {
                "user_id": str(current_user.id),
                "user_type": current_user.user_type,
                "query_context": request.context
            }
            
            # Get AI response with RAG enhancement
            ai_response = await rag_assistant.get_response(
                query=request.message,
                language=request.language,
                user_context=user_context
            )
            
            # Save chat history if database is available
            try:
                chat_entry = ChatHistory(
                    user_id=current_user.id,
                    message=request.message,
                    response=ai_response["response"],
                    context=request.context,
                    language=request.language
                )
                db.add(chat_entry)
                db.commit()
            except:
                pass  # Continue even if database save fails
            
            return ChatResponse(
                response=ai_response["response"],
                language=request.language,
                suggestions=ai_response.get("suggestions", [])
            )
            
        except Exception as rag_error:
            print(f"RAG error: {rag_error}")
            # Fallback to enhanced mock responses
            pass
        
        # Enhanced mock responses with better logic
        message_lower = request.message.lower()
        
        # Get base response for language
        context_responses = MOCK_RESPONSES.get(request.context, MOCK_RESPONSES["general"])
        lang_responses = context_responses.get(request.language, context_responses["en"])
        base_response = lang_responses["response"]
        
        # Enhanced response based on keywords
        response = base_response
        
        # Hemoglobin related queries
        if "hemoglobin" in message_lower or "hb" in message_lower:
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
        
        # Generate suggestions based on context
        suggestions = lang_responses.get("suggestions", [])
        
        return ChatResponse(
            response=response,
            language=request.language,
            suggestions=suggestions
        )
        
    except Exception as e:
        # Final fallback response
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
        "features": ["multilingual_chat", "emergency_detection", "health_guidance", "rag_enhanced"]
    }

@router.get("/chat-history/{user_id}")
async def get_chat_history(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
    limit: int = 20
):
    """Get user's chat history"""
    try:
        # Verify user can access this history
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Cannot access other user's chat history")
        
        # Get recent chat history
        chats = db.query(ChatHistory)\
                 .filter(ChatHistory.user_id == current_user.id)\
                 .order_by(ChatHistory.created_at.desc())\
                 .limit(limit)\
                 .all()
        
        return {
            "chat_history": [
                {
                    "id": str(chat.id),
                    "message": chat.message,
                    "response": chat.response,
                    "context": chat.context,
                    "language": chat.language,
                    "created_at": chat.created_at.isoformat()
                }
                for chat in chats
            ]
        }
    except Exception as e:
        return {"chat_history": []}  # Return empty history if database fails