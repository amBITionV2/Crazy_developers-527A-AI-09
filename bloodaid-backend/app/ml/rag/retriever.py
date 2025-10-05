from typing import List, Dict, Optional
import json

class MockRAGRetriever:
    """Mock RAG retriever for BloodAid knowledge base"""
    
    def __init__(self):
        # Mock knowledge base
        self.knowledge_base = [
            {
                "text": "Blood group O- is the universal donor. It can be given to patients of any blood group.",
                "metadata": {"category": "blood_types", "source": "medical_kb"}
            },
            {
                "text": "Thalassemia patients require regular blood transfusions every 2-3 weeks.",
                "metadata": {"category": "chronic_conditions", "source": "medical_kb"}
            },
            {
                "text": "Minimum weight requirement for blood donation in India is 50 kg (110 lbs).",
                "metadata": {"category": "eligibility", "source": "medical_kb"}
            },
            {
                "text": "Hemoglobin level must be at least 12.5 g/dL for donation.",
                "metadata": {"category": "health_requirements", "source": "medical_kb"}
            },
            {
                "text": "Wait 28 days after COVID-19 recovery before donating blood.",
                "metadata": {"category": "eligibility", "source": "medical_kb"}
            },
            {
                "text": "Dialysis patients may need blood transfusions due to anemia from kidney disease.",
                "metadata": {"category": "chronic_conditions", "source": "medical_kb"}
            },
            {
                "text": "eRaktKosh is India's national blood bank management system.",
                "metadata": {"category": "system_info", "source": "bloodaid_kb"}
            },
            {
                "text": "Blood donation takes about 10-15 minutes for the actual donation process.",
                "metadata": {"category": "process", "source": "bloodaid_kb"}
            }
        ]
    
    def retrieve(
        self,
        query: str,
        n_results: int = 3,
        filter_category: str = None
    ) -> List[Dict]:
        """Retrieve relevant documents for a query"""
        
        # Simple keyword matching (in real implementation, use embeddings)
        query_lower = query.lower()
        
        relevant_docs = []
        for doc in self.knowledge_base:
            # Check category filter
            if filter_category and doc["metadata"].get("category") != filter_category:
                continue
            
            # Simple relevance scoring based on keyword overlap
            doc_text_lower = doc["text"].lower()
            score = 0
            
            # Check for exact matches
            if any(word in doc_text_lower for word in query_lower.split()):
                score += 1
            
            # Specific keyword matching
            if "blood group" in query_lower and "blood group" in doc_text_lower:
                score += 2
            if "thalassemia" in query_lower and "thalassemia" in doc_text_lower:
                score += 2
            if "hemoglobin" in query_lower and "hemoglobin" in doc_text_lower:
                score += 2
            if "eligibility" in query_lower and "eligibility" in doc["metadata"].get("category", ""):
                score += 2
            if "dialysis" in query_lower and "dialysis" in doc_text_lower:
                score += 2
            
            if score > 0:
                relevant_docs.append({
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "distance": 1.0 - (score * 0.2)  # Lower distance = higher relevance
                })
        
        # Sort by relevance (lower distance = more relevant)
        relevant_docs.sort(key=lambda x: x["distance"])
        
        return relevant_docs[:n_results]
    
    def get_context_for_llm(self, query: str, n_results: int = 3) -> str:
        """Get formatted context for LLM prompt"""
        docs = self.retrieve(query, n_results)
        
        if not docs:
            return ""
        
        context = "Relevant medical information:\n\n"
        for i, doc in enumerate(docs, 1):
            context += f"{i}. {doc['text']}\n\n"
        
        return context

# Singleton instance
_retriever_instance = None

def get_rag_retriever() -> MockRAGRetriever:
    """Get or create RAG retriever instance"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = MockRAGRetriever()
    return _retriever_instance