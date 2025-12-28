#!/usr/bin/env python3
"""
FastAPI server for NCERT Doubt Solver RAG Pipeline
Supports cross-language queries: user's preferred language determines response language
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from opea_microservices.retrieval.vector_store import OPEAVectorStore
from opea_microservices.orchestration.rag_orchestrator import OPEARAGOrchestrator
from opea_microservices.llm.mistral_service import MistralConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================
# Request/Response Models
# ========================
class QueryRequest(BaseModel):
    """Request model for RAG query with language preference"""
    query: str
    grade: int
    subject: str
    language: Optional[str] = "english"  # User's preferred response language
    top_k: Optional[int] = 3

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is photosynthesis?",
                "grade": 6,
                "subject": "science",
                "language": "hindi",  # Response will be in Hindi
                "top_k": 3
            }
        }

class Citation(BaseModel):
    """Rich citation information for display"""
    id: int
    source: str
    chapter: str
    section: str
    page: int
    excerpt: str
    relevance: float
    chunk_id: str

class SourceChunk(BaseModel):
    """Full source chunk for detailed view"""
    chunk_id: str
    full_text: str
    metadata: Dict[str, Any]
    relevance: float

class QueryMetadata(BaseModel):
    """Query processing metadata"""
    grade: int
    subject: str
    language: str  # Response language
    query_language: str  # Detected query language
    model: str
    tokens_used: int
    confidence: float
    chunks_retrieved: int
    processing_time_ms: int

class QueryResponse(BaseModel):
    """Response model for RAG query"""
    answer: str
    metadata: QueryMetadata
    citations: List[Citation]
    source_chunks: List[SourceChunk]

class ModelInfo(BaseModel):
    """Model information"""
    model: str
    quantization: str
    size_gb: float
    context_window: int
    gpu_enabled: bool
    gpu_type: str
    n_gpu_layers: int
    languages_supported: List[str]

# ========================
# Initialize FastAPI App
# ========================
app = FastAPI(
    title="NCERT Doubt Solver - RAG API",
    description="Multilingual RAG API: Ask in any language, get response in your preferred language",
    version="2.1.0"
)

# Global instances
rag_orchestrator: Optional[OPEARAGOrchestrator] = None
vector_store: Optional[OPEAVectorStore] = None

# ========================
# Helper Functions
# ========================
def detect_query_language(query: str) -> str:
    """Detect language of query for logging/analytics"""
    return "hindi" if not query.isascii() else "english"

def format_citations(retrieved_chunks: List[Dict], grade: int, subject: str) -> List[Dict]:
    """Transform retrieved_chunks into rich, display-ready citations"""
    citations = []
    
    for idx, chunk in enumerate(retrieved_chunks):
        metadata = chunk.get('metadata', {})
        chapter = metadata.get('chapter', 'Unknown')
        section = metadata.get('section', 'General')
        
        if chapter == 'Unknown' and section != 'General':
            chapter = section
        
        full_text = chunk.get('text', '')
        excerpt = full_text[:150].strip()
        if len(full_text) > 150:
            excerpt += "..."
        
        distance = chunk.get('distance', 0.5)
        relevance = round(1 - distance, 3)
        
        subject_title = subject.replace('_', ' ').title()
        source = f"NCERT {subject_title} Grade {grade}"
        
        citation = {
            "id": idx + 1,
            "source": source,
            "chapter": chapter,
            "section": section,
            "page": metadata.get('page_num', 0),
            "excerpt": excerpt,
            "relevance": relevance,
            "chunk_id": chunk.get('chunk_id', '')
        }
        citations.append(citation)
    
    citations.sort(key=lambda x: x['relevance'], reverse=True)
    for idx, citation in enumerate(citations):
        citation['id'] = idx + 1
    
    return citations

def format_source_chunks(retrieved_chunks: List[Dict]) -> List[Dict]:
    """Format full chunks for detailed viewing"""
    chunks = []
    
    for chunk in retrieved_chunks:
        metadata = chunk.get('metadata', {})
        distance = chunk.get('distance', 0.5)
        
        formatted_chunk = {
            "chunk_id": chunk.get('chunk_id', ''),
            "full_text": chunk.get('text', ''),
            "metadata": {
                "page": metadata.get('page_num', 0),
                "chapter": metadata.get('chapter', 'Unknown'),
                "section": metadata.get('section', 'General'),
                "token_count": metadata.get('token_count', 0),
                "grade": metadata.get('grade', 0),
                "subject": metadata.get('subject', ''),
                "source_file": metadata.get('meta_source_file', '')
            },
            "relevance": round(1 - distance, 3)
        }
        chunks.append(formatted_chunk)
    
    chunks.sort(key=lambda x: x['relevance'], reverse=True)
    return chunks

# ========================
# Startup/Shutdown Events
# ========================
@app.on_event("startup")
async def startup_event():
    """Initialize RAG components on startup"""
    global rag_orchestrator, vector_store
    
    try:
        logger.info("🚀 Starting up Multilingual RAG API...")
        
        vector_store_path = project_root / "data" / "chroma_db"
        logger.info(f"Initializing vector store at {vector_store_path}...")
        vector_store = OPEAVectorStore(persist_directory=str(vector_store_path))
        logger.info("✓ Vector store initialized")
        
        logger.info("Initializing RAG orchestrator...")
        mistral_config = MistralConfig(
            model_path=str(project_root / "models" / "mistral-7b-instruct-v0.2.gguf")
        )
        
        embedding_model = "intfloat/multilingual-e5-large"
        logger.info(f"Using embedding model: {embedding_model} (multilingual, 1024 dims)")
        
        rag_orchestrator = OPEARAGOrchestrator(
            embedding_model_name=embedding_model,
            vector_store=vector_store,
            use_mistral=True,
            mistral_config=mistral_config
        )
        logger.info("✓ RAG orchestrator initialized")
        logger.info("✅ Multilingual RAG API ready! (English ⇄ Hindi)")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down RAG API...")
    if vector_store:
        vector_store.persist()
    logger.info("✓ Cleanup complete")

# ========================
# API Endpoints
# ========================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API status"""
    return {
        "status": "online",
        "service": "NCERT Doubt Solver - Multilingual RAG API",
        "version": "2.1.0",
        "features": {
            "cross_language_support": True,
            "supported_languages": ["english", "hindi"],
            "note": "Ask in any language, respond in user's preferred language"
        },
        "endpoints": {
            "query": "POST /query",
            "model_info": "GET /model-info",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    if rag_orchestrator is None or vector_store is None:
        raise HTTPException(status_code=503, detail="RAG components not initialized")
    
    return {
        "status": "healthy",
        "vector_store_ready": vector_store is not None,
        "llm_ready": rag_orchestrator is not None,
        "total_documents": vector_store.collection.count() if vector_store else 0,
        "multilingual_support": True
    }

@app.post("/query", response_model=QueryResponse, tags=["RAG Query"])
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process a query using the RAG pipeline with cross-language support.
    
    **Cross-Language Feature:**
    - Query language is auto-detected (English/Hindi)
    - Response language is controlled by 'language' parameter
    - Example: Ask in English, get Hindi response (or vice versa)
    
    **Parameters:**
    - **query**: Student's question (any language)
    - **grade**: Grade level (5-10)
    - **subject**: Subject name (e.g., "science", "mathematics")
    - **language**: Response language ("english" or "hindi") - OVERRIDES query language
    - **top_k**: Number of chunks to retrieve (default: 3)
    
    **Returns:**
    - **answer**: Generated answer in requested language
    - **metadata**: Processing info including both query and response language
    - **citations**: Source citations from NCERT textbooks
    - **source_chunks**: Full source chunks for detailed view
    """
    
    if rag_orchestrator is None:
        raise HTTPException(status_code=503, detail="RAG orchestrator not initialized")
    
    start_time = time.time()
    
    try:
        # ✅ Detect query language (for logging/analytics only)
        query_language = detect_query_language(request.query)
        
        # ✅ User's preferred response language (from settings/profile)
        # This ALWAYS determines the response language
        response_language = request.language or "english"
        
        # Optimize top_k for Hindi responses
        adjusted_top_k = min(request.top_k, 3) if response_language.lower() in ["hindi", "hi"] else request.top_k
        
        logger.info(f"📝 Query: '{request.query[:50]}...'")
        logger.info(f"🔍 Query Language (detected): {query_language}")
        logger.info(f"🎯 Response Language (user preference): {response_language}")
        logger.info(f"📚 Grade: {request.grade}, Subject: {request.subject}, top_k: {adjusted_top_k}")
        
        # ✅ Process query with user's preferred response language
        rag_response = rag_orchestrator.process_query(
            query=request.query,
            grade=request.grade,
            subject=request.subject,
            top_k=adjusted_top_k,
            language=response_language  # ✅ User's preference, not auto-detected
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        tokens_used = 512
        if hasattr(rag_orchestrator.llm_service, 'config'):
            tokens_used = rag_orchestrator.llm_service.config.max_tokens
        
        formatted_citations = format_citations(
            rag_response.retrieved_chunks,
            request.grade,
            request.subject
        )
        
        source_chunks = format_source_chunks(rag_response.retrieved_chunks)
        
        logger.info(f"✓ Query processed in {processing_time_ms}ms")
        logger.info(f"✓ Response language: {response_language}")
        
        return QueryResponse(
            answer=rag_response.answer,
            metadata=QueryMetadata(
                grade=request.grade,
                subject=request.subject,
                language=response_language,  # Response language
                query_language=query_language,  # Detected query language
                model="Mistral-7B-Instruct-v0.2",
                tokens_used=tokens_used,
                confidence=rag_response.confidence,
                chunks_retrieved=len(rag_response.retrieved_chunks),
                processing_time_ms=processing_time_ms
            ),
            citations=formatted_citations,
            source_chunks=source_chunks
        )
        
    except Exception as e:
        logger.error(f"❌ Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/model-info", response_model=ModelInfo, tags=["Model Info"])
async def get_model_info():
    """Get information about the LLM model and multilingual support"""
    
    if rag_orchestrator is None or rag_orchestrator.llm_service is None:
        raise HTTPException(status_code=503, detail="LLM service not initialized")
    
    try:
        model_info = rag_orchestrator.llm_service.get_model_info()
        
        return ModelInfo(
            model=model_info['model'],
            quantization=model_info['quantization'],
            size_gb=model_info['size_gb'],
            context_window=model_info['context_window'],
            gpu_enabled=model_info['gpu_enabled'],
            gpu_type=model_info['gpu_type'],
            n_gpu_layers=model_info['n_gpu_layers'],
            languages_supported=model_info.get('languages_supported', ['English', 'Hindi'])
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

# ========================
# Error Handlers
# ========================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

# ========================
# Run Server
# ========================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("Starting NCERT Doubt Solver - Multilingual RAG API v2.1")
    logger.info("=" * 60)
    logger.info("✨ Features:")
    logger.info("  • Cross-language support (English ⇄ Hindi)")
    logger.info("  • User language preference controls response")
    logger.info("  • Ask in any language, respond in preferred language")
    logger.info("=" * 60)
    logger.info("📚 API Documentation: http://localhost:8000/docs")
    logger.info("🔍 Alternative Docs: http://localhost:8000/redoc")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
