# Paste the script above here
#!/usr/bin/env python3
"""
Rebuild Vector Store with Multilingual Embeddings
This script re-embeds all chunks using a multilingual model and rebuilds the vector store.
"""

import sys
import json
import shutil
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from opea_microservices.retrieval.vector_store import OPEAVectorStore


def load_chunks_without_embeddings(file_path: Path):
    """Load chunks and remove old embeddings"""
    with open(file_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Remove old embeddings
    for chunk in chunks:
        if 'embedding' in chunk:
            del chunk['embedding']
    
    return chunks


def generate_multilingual_embeddings(chunks, model_name="intfloat/multilingual-e5-large"):
    """
    Generate embeddings using multilingual model.
    
    Model options:
    - intfloat/multilingual-e5-large (1024 dims) - RECOMMENDED for Hindi
    - sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (768 dims)
    - BAAI/bge-m3 (1024 dims) - Very large, best quality
    """
    print(f"\n📦 Loading multilingual embedding model: {model_name}")
    print("   This may take a few minutes on first run...")
    
    model = SentenceTransformer(model_name)
    
    print(f"\n🔄 Generating embeddings for {len(chunks)} chunks...")
    
    # Extract texts
    texts = [chunk['text'] for chunk in chunks]
    
    # Generate embeddings with progress bar
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        convert_to_numpy=True
    )
    
    # Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk['embedding'] = embedding.tolist()
    
    return chunks


def main():
    print("="*70)
    print("  REBUILD VECTOR STORE WITH MULTILINGUAL EMBEDDINGS")
    print("="*70)
    
    # Paths
    vector_store_path = project_root / "data" / "chroma_db"
    backup_path = project_root / "data" / "chroma_db_backup_english"
    
    embedded_files = [
        project_root / "data/processed/embeddings/6_science_english_embedded.json",
        project_root / "data/processed/embeddings/6_science_hindi_embedded.json"
    ]
    
    # Check if files exist
    missing_files = [f for f in embedded_files if not f.exists()]
    if missing_files:
        print(f"\n❌ ERROR: Missing embedding files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\n💡 Please run your data ingestion pipeline first.")
        return
    
    # Backup existing vector store
    if vector_store_path.exists():
        print(f"\n📦 Backing up existing vector store...")
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(vector_store_path, backup_path)
        print(f"   ✓ Backup created at: {backup_path}")
        
        # Remove old vector store
        shutil.rmtree(vector_store_path)
        print(f"   ✓ Removed old vector store")
    
    # Choose multilingual model
    print("\n🌍 Multilingual Embedding Models:")
    print("   1. intfloat/multilingual-e5-large (1024 dims) - RECOMMENDED")
    print("   2. sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (768 dims)")
    print("   3. BAAI/bge-m3 (1024 dims) - Best quality, very large")
    
    choice = input("\nSelect model (1-3) [default: 1]: ").strip() or "1"
    
    model_map = {
        "1": "intfloat/multilingual-e5-large",
        "2": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "3": "BAAI/bge-m3"
    }
    
    embedding_model = model_map.get(choice, model_map["1"])
    print(f"\n✅ Selected: {embedding_model}")
    
    # Load all chunks
    print("\n📂 Loading chunks from files...")
    all_chunks = []
    for file_path in embedded_files:
        chunks = load_chunks_without_embeddings(file_path)
        all_chunks.extend(chunks)
        print(f"   ✓ Loaded {len(chunks)} chunks from {file_path.name}")
    
    print(f"\n📊 Total chunks to process: {len(all_chunks)}")
    
    # Generate new embeddings
    all_chunks = generate_multilingual_embeddings(all_chunks, embedding_model)
    
    # Create new vector store
    print(f"\n🗄️  Creating new vector store...")
    vector_store = OPEAVectorStore(persist_directory=str(vector_store_path))
    
    # Add chunks in batches
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        vector_store.add_chunks(batch)
    
    # Persist
    vector_store.persist()
    
    # Verify
    total_docs = vector_store.collection.count()
    print(f"\n✅ SUCCESS!")
    print(f"   Total documents in vector store: {total_docs}")
    print(f"   Embedding model: {embedding_model}")
    
    # Update instructions
    print("\n" + "="*70)
    print("📝 NEXT STEPS:")
    print("="*70)
    print(f"\n1. Update scripts/api_server.py line 131:")
    print(f'   embedding_model = "{embedding_model}"')
    print("\n2. Restart your API server:")
    print("   python scripts/api_server.py")
    print("\n3. Test with Hindi query:")
    print('''   curl -X POST "http://localhost:8000/query" \\''')
    print('''     -H "Content-Type: application/json" \\''')
    print('''     -d '{''')
    print('''       "query": "प्रकाश संश्लेषण क्या है?",''')
    print('''       "grade": 6,''')
    print('''       "subject": "science"''')
    print('''     }'\n''')
    print("="*70)
    print("\n🎉 Vector store rebuild complete!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Rebuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)