"""
BloodAid AI Chat Enhanced with RAG
Provides context-aware responses using retrieval augmented generation
"""

import json
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from ..llm.inference import get_grok_llm
from ..rag.retriever import get_rag_retriever


class BloodAidRAG:
    """Enhanced AI assistant with RAG for BloodAid"""
    
    def __init__(self):
        self.llm = get_grok_llm()
        self.retriever = get_rag_retriever()
        
        # RAG prompts for different languages
        self.rag_prompts = {
            "en": """You are BloodAid AI, an expert blood donation assistant. Use the provided medical information to give accurate, helpful responses.

Context from medical knowledge base:
{context}

User query: {query}

Guidelines:
- Use only the provided medical information when possible
- Be encouraging about blood donation while emphasizing safety
- If asked about eligibility, refer to official requirements
- For medical conditions, provide supportive information
- Always end with helpful next steps

Response:""",
            
            "hi": """आप BloodAid AI हैं, एक विशेषज्ञ रक्तदान सहायक। प्रदान की गई चिकित्सा जानकारी का उपयोग करके सटीक, सहायक उत्तर दें।

चिकित्सा ज्ञान आधार से संदर्भ:
{context}

उपयोगकर्ता प्रश्न: {query}

दिशानिर्देश:
- जब संभव हो तो केवल प्रदान की गई चिकित्सा जानकारी का उपयोग करें
- सुरक्षा पर जोर देते हुए रक्तदान के लिए प्रोत्साहित करें
- पात्रता के बारे में पूछे जाने पर, आधिकारिक आवश्यकताओं का संदर्भ दें
- चिकित्सा स्थितियों के लिए, सहायक जानकारी प्रदान करें
- हमेशा सहायक अगले कदमों के साथ समाप्त करें

उत्तर:""",
            
            "kn": """ನೀವು BloodAid AI, ಒಬ್ಬ ತಜ್ಞ ರಕ್ತದಾನ ಸಹಾಯಕ. ಒದಗಿಸಿದ ವೈದ್ಯಕೀಯ ಮಾಹಿತಿಯನ್ನು ಬಳಸಿಕೊಂಡು ನಿಖರವಾದ, ಸಹಾಯಕಾರಿ ಪ್ರತಿಕ್ರಿಯೆಗಳನ್ನು ನೀಡಿ.

ವೈದ್ಯಕೀಯ ಜ್ಞಾನ ಮೂಲದಿಂದ ಸಂದರ್ಭ:
{context}

ಬಳಕೆದಾರ ಪ್ರಶ್ನೆ: {query}

ಮಾರ್ಗದರ್ಶನಗಳು:
- ಸಾಧ್ಯವಾದಾಗ ಒದಗಿಸಿದ ವೈದ್ಯಕೀಯ ಮಾಹಿತಿಯನ್ನು ಮಾತ್ರ ಬಳಸಿ
- ಸುರಕ್ಷತೆಯನ್ನು ಒತ್ತಿ ಹೇಳುತ್ತಾ ರಕ್ತದಾನದ ಬಗ್ಗೆ ಪ್ರೋತ್ಸಾಹಿಸಿ
- ಅರ್ಹತೆಯ ಬಗ್ಗೆ ಕೇಳಿದಾಗ, ಅಧಿಕೃತ ಅವಶ್ಯಕತೆಗಳನ್ನು ಉಲ್ಲೇಖಿಸಿ
- ವೈದ್ಯಕೀಯ ಪರಿಸ್ಥಿತಿಗಳಿಗೆ, ಸಹಾಯಕ ಮಾಹಿತಿ ನೀಡಿ
- ಯಾವಾಗಲೂ ಸಹಾಯಕ ಮುಂದಿನ ಹಂತಗಳೊಂದಿಗೆ ಕೊನೆಗೊಳಿಸಿ

ಪ್ರತಿಕ್ರಿಯೆ:""",
            
            "te": """మీరు BloodAid AI, ఒక నిపుణుడు రక్తదాన సహాయకుడు. అందించిన వైద్య సమాచారాన్ని ఉపయోగించి ఖచ్చితమైన, సహాయకరమైన ప్రతిస్పందనలు ఇవ్వండి.

వైద్య జ్ఞాన స్థావరం నుండి సందర్భం:
{context}

వినియోగదారు ప్రశ్న: {query}

మార్గదర్శకాలు:
- సాధ్యమైనప్పుడు అందించిన వైద్య సమాచారాన్ని మాత్రమే ఉపయోగించండి
- భద్రతను నొక్కిచెప్పుతూ రక్తదానం గురించి ప్రోత్సాహించండి
- అర్హత గురించి అడిగినప్పుడు, అధికారిక అవసరాలను సూచించండి
- వైద్య పరిస్థితుల కోసం, సహాయక సమాచారం అందించండి
- ఎల్లప్పుడూ సహాయక తదుపరి దశలతో ముగించండి

ప్రతిస్పందన:""",
            
            "ml": """നിങ്ങൾ BloodAid AI ആണ്, ഒരു വിദഗ്ധ രക്തദാന സഹായി. നൽകിയ മെഡിക്കൽ വിവരങ്ങൾ ഉപയോഗിച്ച് കൃത്യവും സഹായകരവുമായ പ്രതികരണങ്ങൾ നൽകുക.

മെഡിക്കൽ വിജ്ഞാന കേന്ദ്രത്തിൽ നിന്നുള്ള സന്ദർഭം:
{context}

ഉപയോക്തൃ ചോദ്യം: {query}

മാർഗ്ഗനിർദ്ദേശങ്ങൾ:
- സാധ്യമായപ്പോൾ നൽകിയ മെഡിക്കൽ വിവരങ്ങൾ മാത്രം ഉപയോഗിക്കുക
- സുരക്ഷയ്ക്ക് ഊന്നൽ നൽകിക്കൊണ്ട് രക്തദാനത്തെ പ്രോത്സാഹിപ്പിക്കുക
- യോഗ്യതയെക്കുറിച്ച് ചോദിക്കുമ്പോൾ, ഔദ്യോഗിക ആവശ്യകതകൾ പരാമർശിക്കുക
- മെഡിക്കൽ അവസ്ഥകൾക്ക്, സഹായക വിവരങ്ങൾ നൽകുക
- എപ്പോഴും സഹായകരമായ അടുത്ത ഘട്ടങ്ങളോടെ അവസാനിപ്പിക്കുക

പ്രതികരണം:"""
        }
    
    async def get_response(
        self,
        query: str,
        language: str = "en",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get RAG-enhanced response"""
        try:
            # Retrieve relevant context
            context = self.retriever.get_context_for_llm(query, n_results=3)
            
            # Prepare prompt with context
            prompt_template = self.rag_prompts.get(language, self.rag_prompts["en"])
            prompt = prompt_template.format(context=context, query=query)
            
            # Get LLM response
            response = await self.llm.get_response(
                prompt=prompt,
                language=language,
                context_type="rag_enhanced"
            )
            
            # Add RAG metadata
            response["rag_context"] = {
                "context_used": bool(context.strip()),
                "retrieved_docs": len(context.split('\n\n')) - 2 if context.strip() else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return response
            
        except Exception as e:
            # Fallback to regular LLM response
            print(f"RAG error: {str(e)}")
            return await self.llm.get_response(query, language, "general")
    
    def add_knowledge(self, text: str, metadata: Dict[str, Any]):
        """Add new knowledge to the retriever (for future enhancement)"""
        # This would update the knowledge base in a real implementation
        pass

# Singleton instance
_rag_instance = None

def get_bloodaid_rag() -> BloodAidRAG:
    """Get or create BloodAid RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = BloodAidRAG()
    return _rag_instance