# Add imports
from dataclasses import dataclass
from typing import Optional, List, Dict
from sentence_transformers import SentenceTransformer
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from opea_microservices.llm.mistral_service import OPEAMistralService, MistralConfig

@dataclass
class QueryResponse:
    answer: str
    language: str
    confidence: float
    citations: List[Dict]
    retrieved_chunks: List[Dict]

class OPEARAGOrchestrator:
    """OPEA RAG Pipeline Orchestrator - User Language Preference Priority"""
    
    def __init__(
        self,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        vector_store=None,
        use_mistral: bool = True,
        mistral_config: Optional[MistralConfig] = None
    ):
        logger.info("Initializing OPEA RAG Orchestrator...")
        
        # Embedding service
        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name, device="cpu")
        
        # Vector store
        self.vector_store = vector_store
        
        # LLM Service - MISTRAL
        if use_mistral:
            logger.info("Initializing Mistral-7B LLM Service...")
            self.llm_service = OPEAMistralService(config=mistral_config)
            self.llm_type = "mistral"
        else:
            logger.warning("Mistral not available, using fallback")
            self.llm_service = None
            self.llm_type = "fallback"
        
        logger.info("✓ OPEA RAG Orchestrator initialized")
    
    def _translate_hindi_query(self, query: str) -> str:
        """Translate common Hindi science terms to English for better semantic matching"""
        hindi_to_english = {
            "प्रकाश संश्लेषण": "photosynthesis",
            "प्रकाश": "light",
            "संश्लेषण": "synthesis",
            "पौधे": "plants",
            "पत्ते": "leaves",
            "हरा": "green",
            "भोजन": "food",
            "कार्बन डाइऑक्साइड": "carbon dioxide",
            "पानी": "water",
            "सूर्य का प्रकाश": "sunlight",
            "ऑक्सीजन": "oxygen",
            "वायुमंडल": "atmosphere",
            "परावर्तन": "reflection",
            "छाया": "shadow",
            "पारदर्शी": "transparent",
            "अपारदर्शी": "opaque",
            "अर्धपारदर्शी": "translucent"
        }
        
        translated_query = query
        for hindi_term, english_term in hindi_to_english.items():
            if hindi_term in query:
                translated_query = translated_query.replace(hindi_term, english_term)
        
        return translated_query
    
    def _get_hindi_terms(self) -> dict:
        """Get Hindi translations for common science terms"""
        english_to_hindi = {
            "photosynthesis": "प्रकाश संश्लेषण",
            "light": "प्रकाश",
            "plants": "पौधे",
            "leaves": "पत्ते",
            "green": "हरा",
            "food": "भोजन",
            "carbon dioxide": "कार्बन डाइऑक्साइड",
            "water": "पानी",
            "sunlight": "सूर्य का प्रकाश",
            "oxygen": "ऑक्सीजन",
            "atmosphere": "वायुमंडल",
            "reflection": "परावर्तन",
            "shadow": "छाया",
            "transparent": "पारदर्शी",
            "opaque": "अपारदर्शी",
            "translucent": "अर्धपारदर्शी",
            "process": "प्रक्रिया",
            "energy": "ऊर्जा",
            "chlorophyll": "हरितलवक",
            "glucose": "ग्लूकोज",
            "starch": "स्टार्च",
            "production": "उत्पादन",
            "results": "परिणाम",
            "presence": "उपस्थिति",
            "using": "का उपयोग करके",
            "make": "बनाते हैं",
            "their": "अपना",
            "by which": "जिसके द्वारा",
            "is a": "एक",
            "and": "तथा",
            "in the": "में",
            "of": "का",
            "sun": "सूर्य"
        }
        return english_to_hindi
    
    def process_query(
        self,
        query: str,
        grade: int,
        subject: Optional[str] = None,
        top_k: int = 5,
        language: Optional[str] = None
    ) -> QueryResponse:
        """
        Process a query with retrieval and generation.
        
        IMPORTANT: The 'language' parameter (user's preferred language) 
        ALWAYS determines the response language, regardless of query language.
        """
        
        # ✅ PRIORITY: User's preferred language from settings
        # This is what they selected in their profile/settings
        response_language = language or "english"
        
        logger.info(f"🎯 User's preferred response language: {response_language}")
        
        # Translate Hindi query to English for semantic search ONLY
        # (ChromaDB has English NCERT content)
        search_query = query
        if not query.isascii():  # Query contains Hindi characters
            search_query = self._translate_hindi_query(query)
            logger.info(f"Translated query for search: '{search_query}'")
        
        # Generate embedding for search
        query_embedding = self.embedding_model.encode([search_query])[0].tolist()
        
        # Retrieve from ChromaDB (always search English NCERT content)
        retrieved_chunks = self.vector_store.search(
            query_embedding=query_embedding,
            grade=grade,
            subject=subject,
            language="english",  # ChromaDB has English NCERT textbooks
            top_k=top_k
        )
        
        # Format context chunks
        context_chunks = [
            {
                'text': chunk['text'],
                'metadata': chunk['metadata']
            }
            for chunk in retrieved_chunks
        ]
        
        # ✅ Generate answer in USER'S PREFERRED LANGUAGE
        # Not based on query language, but on user's settings
        answer = self.generate_answer(
            query=query,
            context_chunks=context_chunks,
            grade=grade,
            subject=subject or "science",
            language=response_language,  # ✅ USER'S PREFERENCE
            hindi_terms=self._get_hindi_terms() if response_language.lower() in ["hindi", "hi"] else None
        )
        
        # Calculate confidence
        confidence = 0.9
        
        # Extract citations
        citations = [
            {
                'chapter': chunk['metadata'].get('chapter', 'Unknown'),
                'page': chunk['metadata'].get('page_num', 'Unknown')
            }
            for chunk in retrieved_chunks
        ]
        
        return QueryResponse(
            answer=answer,
            language=response_language,  # Return user's preferred language
            confidence=confidence,
            citations=citations,
            retrieved_chunks=retrieved_chunks
        )
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict],
        grade: int,
        subject: str,
        language: str,
        hindi_terms: Optional[Dict] = None
    ) -> str:
        """Generate answer using Mistral-7B in user's preferred language"""
        
        if self.llm_service:
            # ✅ Generate in user's preferred language
            result = self.llm_service.generate_answer(
                query=query,
                context_chunks=context_chunks,
                grade=grade,
                language=language,  # ✅ USER'S PREFERENCE
                subject=subject,
                hindi_terms=hindi_terms
            )
            
            if result['success']:
                logger.info(f"✓ Generated {language} response ({result['tokens_used']} tokens)")
                answer = result['answer']
                
                # Clean citations
                answer = re.sub(r'\[(?:Source|स्रोत|संदर्भ)\s*\d+[^\]]*\]', '', answer)
                answer = re.sub(r'\[.*?(?:Page|पृष्ठ):?\s*\d+.*?\]', '', answer)
                answer = ' '.join(answer.split())
                
                # For Hindi responses, replace English terms
                if language.lower() in ["hindi", "hi"] and hindi_terms:
                    sorted_terms = sorted(hindi_terms.items(), key=lambda x: len(x[0]), reverse=True)
                    for eng_term, hindi_term in sorted_terms:
                        answer = answer.replace(eng_term, hindi_term)
                        answer = answer.replace(eng_term.capitalize(), hindi_term)
                        answer = answer.replace(eng_term.upper(), hindi_term)
                        answer = answer.replace(eng_term.lower(), hindi_term)
                    
                    # Cleanup
                    answer = re.sub(r'\([^)]*[a-zA-Z][^)]*\)', '', answer)
                    answer = ' '.join(answer.split())
                
                return answer
            else:
                logger.error(f"Generation failed: {result.get('error')}")
                return "Error: Could not generate response"
        else:
            return "Error: LLM service not available"
