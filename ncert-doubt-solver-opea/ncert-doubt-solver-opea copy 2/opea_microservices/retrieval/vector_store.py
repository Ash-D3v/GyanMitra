import chromadb
from typing import List, Dict, Optional
import json
from pathlib import Path


class OPEAVectorStore:
    """OPEA Microservice for Vector Storage & Retrieval"""

    def __init__(self, persist_directory: str = "./data/chroma_db"):
        # Use PersistentClient for modern ChromaDB API
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Create collection with metadata filtering
        self.collection = self.client.get_or_create_collection(
            name="ncert_chunks",
            metadata={"hnsw:space": "cosine"}
        )

        print(f"✓ ChromaDB initialized at {persist_directory}")

    def add_chunks(self, embedded_chunks: List[Dict]):
        """Add chunks with embeddings to vector store"""

        ids = [chunk['chunk_id'] for chunk in embedded_chunks]
        embeddings = [chunk['embedding'] for chunk in embedded_chunks]
        documents = [chunk['text'] for chunk in embedded_chunks]

        # ✅ Flatten top-level and nested metadata
        metadatas = []
        for chunk in embedded_chunks:
            meta = {
                'grade': chunk.get('grade'),
                'subject': chunk.get('subject'),
                'language': chunk.get('language'),
                'chapter': chunk.get('chapter', 'Unknown'),
                'page_num': chunk.get('page_num', -1),
                'section': chunk.get('section', 'Unknown'),
                'chunk_index': chunk.get('chunk_index'),
                'token_count': chunk.get('token_count'),
            }

            # Flatten nested 'metadata' dict (avoid nested structure)
            if 'metadata' in chunk and isinstance(chunk['metadata'], dict):
                for key, value in chunk['metadata'].items():
                    meta[f"meta_{key}"] = value

            metadatas.append(meta)

        # Batch upload
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        print(f"✓ Added {len(ids)} chunks to vector store")

    def search(
        self,
        query_embedding: List[float],
        grade: Optional[int] = None,
        subject: Optional[str] = None,
        language: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """Semantic search with metadata filtering"""
        where_conditions = []
        
        if grade is not None:
            where_conditions.append({"grade": {"$eq": grade}})
        if subject:
            where_conditions.append({"subject": {"$eq": subject}})
        if language:
            # Handle case-insensitive language matching
            # Since we have both "Hindi" and "english" in the database
            if language.lower() == "hindi":
                where_conditions.append({"language": {"$eq": "Hindi"}})
            elif language.lower() == "english":
                where_conditions.append({"language": {"$eq": "english"}})
            else:
                where_conditions.append({"language": {"$eq": language}})
            
        where_filter = {"$and": where_conditions} if where_conditions else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter if where_filter else None
        )

        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'chunk_id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        return formatted_results

    def persist(self):
        """Persist database to disk (automatic with PersistentClient)"""
        # PersistentClient automatically persists changes
        print("✓ Vector store persisted (automatic)")


# ========================
# Usage Example
# ========================
if __name__ == "__main__":
    # Get project root directory (two levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    
    vector_store = OPEAVectorStore(
        persist_directory=str(project_root / "data" / "chroma_db")
    )

    # List of embedded JSON files (relative to project root)
    embedded_files = [
        project_root / "data/processed/embeddings/6_science_english_embedded.json",
        project_root / "data/processed/embeddings/ncert_hindi_ocr_embedded.json"
    ]

    # Load and combine all chunks
    all_chunks = []
    for file_path in embedded_files:
        with open(file_path, 'r') as f:
            chunks = json.load(f)
            all_chunks.extend(chunks)
            print(f"✓ Loaded {len(chunks)} chunks from {file_path}")

    # Add all chunks to the vector store
    vector_store.add_chunks(all_chunks)

    # Persist the database
    vector_store.persist()

    # Optional: verify total documents stored
    print(f"Total documents stored: {vector_store.collection.count()}")
