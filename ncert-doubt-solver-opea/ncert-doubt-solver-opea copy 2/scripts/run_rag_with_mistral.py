#!/usr/bin/env python3
"""
Complete RAG pipeline with Mistral-7B
All-in-one script for production use
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict

sys.path.append(str(Path(__file__).parent.parent))

from opea_microservices.retrieval.vector_store import OPEAVectorStore
from opea_microservices.orchestration.rag_orchestrator import OPEARAGOrchestrator
from opea_microservices.llm.mistral_service import MistralConfig
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGSystemManager:
    """Manager for complete RAG system with Mistral"""
    
    def __init__(self, vector_db_path: str = "./data/chroma_db"):
        """Initialize RAG system"""
        
        logger.info("🚀 Initializing RAG System with Mistral-7B...")
        
        # Load vector store
        logger.info("📦 Loading vector database...")
        self.vector_store = OPEAVectorStore(persist_directory=vector_db_path)
        
        # Initialize RAG with Mistral and the SAME embedding model used for the DB
        logger.info("🤖 Loading Mistral-7B model and embedding model...")
        embedding_model = "intfloat/multilingual-e5-large"  # 1024d, matches existing Chroma collection
        logger.info(f"Using embedding model: {embedding_model}")

        self.rag = OPEARAGOrchestrator(
            embedding_model_name=embedding_model,
            vector_store=self.vector_store,
            use_mistral=True,
            mistral_config=MistralConfig(
                n_threads=8,
                n_gpu_layers=35
            )
        )
        
        logger.info("✅ RAG System ready!")
    
    def query(
        self,
        question: str,
        grade: int = 6,
        subject: Optional[str] = None,
        top_k: int = 5,
        verbose: bool = False
    ) -> Dict:
        """Process a query"""
        
        logger.info(f"\n📚 Processing query: {question}")
        logger.info(f"   Grade: {grade}, Subject: {subject}")
        
        response = self.rag.process_query(
            query=question,
            grade=grade,
            subject=subject,
            top_k=top_k
        )
        
        if verbose:
            logger.info(f"Language: {response.language}")
            logger.info(f"Confidence: {response.confidence:.2%}")
            logger.info(f"Retrieved chunks: {len(response.retrieved_chunks)}")
        
        return {
            'question': question,
            'answer': response.answer,
            'language': response.language,
            'confidence': response.confidence,
            'citations': response.citations,
            'grade': grade,
            'subject': subject
        }
    
    def interactive_chat(self):
        """Interactive chat mode"""
        
        print("\n" + "="*70)
        print("NCERT DOUBT-SOLVER (Mistral-7B)")
        print("="*70)
        print("\nInstructions:")
        print("  • Type your question and press Enter")
        print("  • Set grade with 'grade:N' (e.g., grade:8)")
        print("  • Set subject with 'subject:name' (e.g., subject:science)")
        print("  • Type 'quit' to exit")
        print("  • Type 'info' for model information")
        print("="*70 + "\n")
        
        grade = 6
        subject = None
        
        while True:
            try:
                user_input = input("\n📝 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'info':
                    info = self.rag.llm_service.get_model_info()
                    print("\n📊 Model Information:")
                    print(json.dumps(info, indent=2))
                    continue
                
                # Parse commands
                if user_input.startswith('grade:'):
                    try:
                        grade = int(user_input.split(':')[1])
                        print(f"✓ Grade set to {grade}")
                        continue
                    except:
                        print("⚠️  Invalid grade format")
                        continue
                
                if user_input.startswith('subject:'):
                    subject = user_input.split(':', 1)[1].strip()
                    print(f"✓ Subject set to {subject}")
                    continue
                
                # Process query
                result = self.query(user_input, grade, subject, verbose=True)
                
                print(f"\n🤖 Assistant: {result['answer']}")
                
                if result['citations']:
                    print("\n📚 Sources:")
                    for i, cite in enumerate(result['citations'][:3], 1):
                        print(f"   [{i}] {cite['chapter']}, Page {cite['page']}")
                
                print(f"\n📊 Confidence: {result['confidence']:.0%}")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print("⚠️  An error occurred. Please try again.")
    
    def batch_process(self, questions_file: str, output_file: str):
        """Process multiple questions from file"""
        
        logger.info(f"Loading questions from {questions_file}...")
        
        try:
            with open(questions_file, 'r') as f:
                questions = json.load(f)
            
            results = []
            
            for i, q_data in enumerate(questions, 1):
                logger.info(f"Processing question {i}/{len(questions)}...")
                
                result = self.query(
                    question=q_data.get('question'),
                    grade=q_data.get('grade', 6),
                    subject=q_data.get('subject')
                )
                
                results.append(result)
            
            # Save results
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved {len(results)} results to {output_file}")
        
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="NCERT Doubt-Solver with Mistral-7B"
    )
    
    parser.add_argument(
        '--mode',
        choices=['interactive', 'batch', 'single'],
        default='interactive',
        help='Operating mode'
    )
    
    parser.add_argument(
        '--question',
        help='Single question to process (for --mode single)'
    )
    
    parser.add_argument(
        '--grade',
        type=int,
        default=6,
        help='Student grade (5-10)'
    )
    
    parser.add_argument(
        '--subject',
        help='Subject name'
    )
    
    parser.add_argument(
        '--input',
        help='Input file with questions (for --mode batch)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for batch results'
    )
    
    parser.add_argument(
        '--vector-db',
        default='../data/chroma_db',
        help='Path to vector database'
    )
    
    args = parser.parse_args()
    
    # Initialize system
    rag_system = RAGSystemManager(vector_db_path=args.vector_db)
    
    # Mode: Single query
    if args.mode == 'single':
        if not args.question:
            print("❌ Please provide --question")
            return
        
        result = rag_system.query(
            args.question,
            grade=args.grade,
            subject=args.subject,
            verbose=True
        )
        
        print(f"\n{result['answer']}")
        
        if result['citations']:
            print("\nCitations:")
            for cite in result['citations']:
                print(f"  • {cite['chapter']}, Page {cite['page']}")
    
    # Mode: Batch processing
    elif args.mode == 'batch':
        if not args.input or not args.output:
            print("❌ Please provide --input and --output")
            return
        
        rag_system.batch_process(args.input, args.output)
    
    # Mode: Interactive
    else:
        rag_system.interactive_chat()


if __name__ == "__main__":
    main()