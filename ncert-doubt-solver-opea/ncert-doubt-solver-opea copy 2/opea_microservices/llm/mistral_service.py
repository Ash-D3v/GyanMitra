import os
import logging
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from llama_cpp import Llama
import torch

logger = logging.getLogger(__name__)

@dataclass
class MistralConfig:
    """Configuration for Mistral-7B LLM Service"""
    model_path: str = "../models/mistral-7b-instruct-v0.2.gguf"
    n_ctx: int = 4096  # Context window (increased for Hindi support)
    n_threads: int = 8  # CPU threads for M2
    n_gpu_layers: int = 0  # CPU only
    temperature: float = 0.3
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 512
    verbose: bool = False

class OPEAMistralService:
    """OPEA LLM Microservice using Mistral-7B with Multilingual Support"""
    
    def __init__(self, config: Optional[MistralConfig] = None):
        self.config = config or MistralConfig()
        
        logger.info(f"Initializing Mistral-7B Service...")
        logger.info(f"Model: {self.config.model_path}")
        
        # Check model exists
        if not Path(self.config.model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {self.config.model_path}\n"
                f"Download from: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
            )
        
        # Initialize Mistral
        try:
            logger.info("Loading model...")
            self.model = Llama(
                model_path=self.config.model_path,
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                n_gpu_layers=self.config.n_gpu_layers,
                verbose=self.config.verbose
            )
            if self.config.n_gpu_layers > 0:
                logger.info("✓ Model loaded successfully with GPU acceleration")
                self.gpu_enabled = True
            else:
                logger.info("✓ Model loaded successfully (CPU mode)")
                self.gpu_enabled = False
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise
    
    def build_mistral_prompt(
        self,
        query: str,
        context_chunks: List[Dict],
        grade: int,
        language: str,
        subject: str = "science",
        hindi_terms: Optional[Dict] = None
    ) -> str:
        """Build prompt in Mistral's instruction format with language support"""
        
        # ✅ Determine if we need Hindi response
        is_hindi_query = language.lower() in ["hindi", "hi"]
        
        # ✅ Build context text
        max_context_chars = 3500  # Leave room for instructions
        context_text = ""
        total_chars = 0
        
        for i, chunk in enumerate(context_chunks, 1):
            chunk_text = chunk['text']
            
            # Truncate individual chunks if too long
            if len(chunk_text) > 800:
                chunk_text = chunk_text[:800] + "..."
            
            # Add context (no source labels in text)
            chunk_content = f"संदर्भ {i}:\n{chunk_text}\n\n" if is_hindi_query else f"Context {i}:\n{chunk_text}\n\n"
            
            if total_chars + len(chunk_content) > max_context_chars:
                break
            
            context_text += chunk_content
            total_chars += len(chunk_content)
        
        # ✅ Language-specific system instructions
        if is_hindi_query:
            system_instruction = f"""आप Grade {grade} के छात्रों के लिए एक विशेषज्ञ NCERT {subject} पाठ्यपुस्तक शिक्षक हैं।

बहुत महत्वपूर्ण निर्देश:
1. उत्तर केवल हिंदी में दें (देवनागरी लिपि में)
2. अंग्रेजी शब्दों का बिल्कुल प्रयोग न करें
3. वैज्ञानिक शब्दों के लिए हिंदी पारिभाषिक शब्दों का प्रयोग करें
4. केवल दिए गए संदर्भ के आधार पर उत्तर दें
5. उत्तर में [Source] या [स्रोत] टैग न लिखें
6. सरल और स्पष्ट भाषा में लिखें
7. Grade {grade} के छात्रों के स्तर के अनुसार उत्तर दें"""
            
            # Add Hindi terminology if provided
            if hindi_terms:
                terms_text = "\n\nहिंदी शब्दावली (केवल संदर्भ के लिए):\n"
                for eng, hindi in list(hindi_terms.items())[:15]:
                    terms_text += f"• {eng} = {hindi}\n"
                system_instruction += terms_text
            
            context_header = "NCERT पाठ्यपुस्तक से संदर्भ सामग्री:"
            question_header = "छात्र का प्रश्न:"
            answer_instruction = "उत्तर (केवल हिंदी में, बिना किसी स्रोत उद्धरण के):"
            
        else:  # English
            system_instruction = f"""You are an expert NCERT textbook tutor for Grade {grade} {subject} students.

CRITICAL INSTRUCTIONS:
1. Answer in English only
2. Answer ONLY the student's specific question
3. Base your answer ONLY on the provided context
4. Do NOT include [Source X] or citations within your answer text
5. Write in clear, flowing paragraphs
6. Keep your answer suitable for Grade {grade} students
7. If context doesn't contain the answer, say "I don't have enough information"
8. Do NOT answer any example questions found in the context"""
            
            context_header = "Reference Material from NCERT Textbooks:"
            question_header = "Student's Question:"
            answer_instruction = "Answer (in English, without source citations in text):"
        
        # ✅ Build Mistral instruction format prompt
        prompt = f"""[INST] {system_instruction}

{context_header}
{context_text}

{question_header} {query}

{answer_instruction} [/INST]"""
        
        # Log for debugging
        logger.info(f"🔤 Language: {language}")
        logger.info(f"📝 Prompt length: {len(prompt)} chars")
        logger.info(f"📝 Prompt preview: {prompt[:400]}...")
        
        return prompt
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict],
        grade: int = 6,
        language: str = "english",
        subject: str = "science",
        hindi_terms: Optional[Dict] = None
    ) -> Dict:
        """Generate answer using Mistral-7B with language support"""
        
        # Build language-aware prompt
        prompt = self.build_mistral_prompt(
            query=query,
            context_chunks=context_chunks,
            grade=grade,
            language=language,
            subject=subject,
            hindi_terms=hindi_terms
        )
        
        logger.info(f"🤖 Generating {language} response...")
        
        try:
            # Generate with Mistral
            response = self.model(
                prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                stop=["[INST]", "Student:", "Context:", "संदर्भ:", "छात्र का प्रश्न:"],
                echo=False
            )
            
            answer_text = response['choices'][0]['text'].strip()
            
            # ✅ Post-process to remove any remaining citations
            import re
            answer_text = re.sub(r'\[(?:Source|स्रोत|संदर्भ)\s*\d+[^\]]*\]', '', answer_text)
            answer_text = re.sub(r'\[.*?(?:Page|पृष्ठ):?\s*\d+.*?\]', '', answer_text)
            answer_text = ' '.join(answer_text.split())  # Clean extra spaces
            
            # ✅ For Hindi, verify response is actually in Hindi
            if language.lower() in ["hindi", "hi"]:
                # Check if response has significant English content
                english_words = re.findall(r'[a-zA-Z]{4,}', answer_text)
                if len(english_words) > 5:  # More than 5 English words
                    logger.warning(f"⚠️ Hindi response contains {len(english_words)} English words")
                    # Try to replace with Hindi terms if provided
                    if hindi_terms:
                        for eng, hindi in sorted(hindi_terms.items(), key=lambda x: len(x[0]), reverse=True):
                            answer_text = re.sub(r'\b' + re.escape(eng) + r'\b', hindi, answer_text, flags=re.IGNORECASE)
            
            tokens_used = response['usage']['completion_tokens']
            
            logger.info(f"✓ Generated {language} response ({tokens_used} tokens)")
            
            return {
                'answer': answer_text,
                'tokens_used': tokens_used,
                'model': 'Mistral-7B-Instruct-v0.2',
                'success': True
            }
        
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return {
                'answer': "Error: Could not generate response",
                'tokens_used': 0,
                'model': 'Mistral-7B-Instruct-v0.2',
                'success': False,
                'error': str(e)
            }
    
    def stream_answer(
        self,
        query: str,
        context_chunks: List[Dict],
        grade: int = 6,
        language: str = "english",
        subject: str = "science"
    ):
        """Stream answer tokens for real-time display"""
        
        prompt = self.build_mistral_prompt(
            query=query,
            context_chunks=context_chunks,
            grade=grade,
            language=language,
            subject=subject
        )
        
        # Stream generation
        for token in self.model(
            prompt,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            stream=True
        ):
            yield token['choices'][0]['text']
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model': 'Mistral-7B-Instruct-v0.2',
            'quantization': 'Q4_K_M (4-bit)',
            'size_gb': 4.1,
            'context_window': self.config.n_ctx,
            'gpu_enabled': self.gpu_enabled,
            'gpu_type': 'Metal (M2 Mac)' if self.gpu_enabled else 'CPU',
            'n_gpu_layers': self.config.n_gpu_layers if self.gpu_enabled else 0,
            'languages_supported': ['English', 'Hindi']
        }


# ============ Usage Example ============
if __name__ == "__main__":
    import json
    
    # Initialize service
    mistral_service = OPEAMistralService()
    
    # Print model info
    print("\n📊 Model Information:")
    print(json.dumps(mistral_service.get_model_info(), indent=2))
    
    # Test English
    test_context_en = [
        {
            'chunk_id': 'test_001',
            'text': 'Natural numbers are numbers used for counting: 1, 2, 3, 4, ...',
            'metadata': {
                'chapter': 'Chapter 1: Numbers',
                'page_num': 5,
                'grade': 6,
                'subject': 'mathematics'
            }
        }
    ]
    
    result_en = mistral_service.generate_answer(
        query="What are natural numbers?",
        context_chunks=test_context_en,
        grade=6,
        language="english"
    )
    
    print("\n💬 English Answer:")
    print(result_en['answer'])
    print(f"📈 Tokens: {result_en['tokens_used']}")
    
    # Test Hindi
    hindi_terms = {
        "natural numbers": "प्राकृतिक संख्याएँ",
        "counting": "गिनती",
        "numbers": "संख्याएँ"
    }
    
    result_hi = mistral_service.generate_answer(
        query="प्राकृतिक संख्याएँ क्या हैं?",
        context_chunks=test_context_en,
        grade=6,
        language="hindi",
        hindi_terms=hindi_terms
    )
    
    print("\n💬 Hindi Answer:")
    print(result_hi['answer'])
    print(f"📈 Tokens: {result_hi['tokens_used']}")
