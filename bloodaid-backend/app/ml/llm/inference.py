import openai
from typing import List, Dict, Optional
from app.config.settings import settings

class GrokLLM:
    """Grok LLM integration for BloodAid"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.GROK_API_KEY,
            base_url=settings.GROK_BASE_URL
        )
        self.model = "grok-beta"
    
    def generate_response(
        self,
        query: str,
        language: str = "en",
        context_type: str = "general",
        rag_context: str = "",
        max_tokens: int = 300
    ) -> str:
        """Generate response using Grok API"""
        
        # Language mapping
        lang_map = {
            "en": "English",
            "hi": "Hindi", 
            "kn": "Kannada",
            "te": "Telugu",
            "ml": "Malayalam"
        }
        
        # Build system prompt
        system_prompt = f"""You are BloodAid AI Assistant, an expert in blood donation and health management.
Always respond in {lang_map.get(language, 'English')}.

Context: {context_type}
{rag_context}

Guidelines:
- Be empathetic and supportive
- Provide accurate medical information
- Include medical disclaimers when appropriate
- For emergencies, prioritize urgent help
- Use simple, clear language
- Include relevant blood donation facts
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Grok API error: {e}")
            return self._get_fallback_response(query, language, context_type)
    
    def _get_fallback_response(self, query: str, language: str, context_type: str) -> str:
        """Fallback response when API fails"""
        fallback_responses = {
            "en": {
                "emergency": "I understand this is urgent. Please contact your nearest hospital or blood bank immediately. For emergency assistance, call emergency services.",
                "health": "For health-related questions, I recommend consulting with a qualified medical professional. They can provide personalized advice based on your specific situation.",
                "donation": "Thank you for your interest in blood donation! For accurate information about donation requirements and procedures, please contact your local blood bank.",
                "general": "I'm here to help with blood donation and health questions. Please try asking your question again or contact support if the issue persists."
            },
            "hi": {
                "emergency": "मैं समझता हूं यह जरूरी है। कृपया अपने निकटतम अस्पताल या ब्लड बैंक से तुरंत संपर्क करें।",
                "health": "स्वास्थ्य संबंधी सवालों के लिए, मैं किसी योग्य डॉक्टर से सलाह लेने की सिफारिश करता हूं।",
                "donation": "रक्तदान में आपकी रुचि के लिए धन्यवाद! सटीक जानकारी के लिए अपने स्थानीय ब्लड बैंक से संपर्क करें।",
                "general": "मैं रक्तदान और स्वास्थ्य के सवालों में मदद के लिए यहां हूं। कृपया दोबारा पूछें।"
            }
        }
        
        lang_responses = fallback_responses.get(language, fallback_responses["en"])
        return lang_responses.get(context_type, lang_responses["general"])
    
    async def get_response(
        self,
        prompt: str,
        language: str = "en",
        context_type: str = "general",
        max_tokens: int = 300
    ) -> Dict[str, any]:
        """Async wrapper for generate_response with structured output"""
        try:
            response_text = self.generate_response(
                query=prompt,
                language=language,
                context_type=context_type,
                max_tokens=max_tokens
            )
            
            return {
                "response": response_text,
                "language": language,
                "context_type": context_type,
                "suggestions": self._generate_suggestions(context_type, language)
            }
        except Exception as e:
            print(f"Error in get_response: {e}")
            return {
                "response": self._get_fallback_response("", language, context_type),
                "language": language,
                "context_type": context_type,
                "suggestions": []
            }
    
    def _generate_suggestions(self, context_type: str, language: str) -> List[str]:
        """Generate helpful suggestions based on context"""
        suggestions = {
            "emergency": ["Find donors near me", "Emergency blood banks", "Contact hospital", "Send SOS alert"],
            "health": ["Check eligibility", "Hemoglobin tips", "Health tracking", "Chronic conditions"],
            "donation": ["Find centers", "Schedule donation", "Track history", "Learn process"],
            "general": ["Emergency help", "Donate blood", "Health check", "Find donors"]
        }
        
        return suggestions.get(context_type, suggestions["general"])

# Singleton instance
_llm_instance = None

def get_llm() -> GrokLLM:
    """Get or create LLM instance"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = GrokLLM()
    return _llm_instance

def get_grok_llm() -> GrokLLM:
    """Get or create Grok LLM instance (alias for compatibility)"""
    return get_llm()