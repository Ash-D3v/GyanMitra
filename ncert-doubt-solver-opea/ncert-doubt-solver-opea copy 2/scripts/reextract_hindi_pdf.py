#!/usr/bin/env python3
"""
Re-extract Hindi PDF with improved OCR settings
"""

import os
import json
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm

# Improved Tesseract config for Hindi
TESSERACT_CONFIG = '--oem 1 --psm 6 -c preserve_interword_spaces=1'

def extract_hindi_pdf_improved(pdf_path: str, output_path: str, dpi: int = 300):
    """
    Extract Hindi PDF with improved settings
    
    Args:
        pdf_path: Path to Hindi PDF
        output_path: Where to save extracted JSON
        dpi: Image resolution (higher = better quality, slower)
    """
    print(f"🔄 Converting PDF to images (DPI: {dpi})...")
    images = convert_from_path(pdf_path, dpi=dpi)
    
    print(f"📝 Extracting text from {len(images)} pages...")
    extracted_pages = []
    
    for page_num, image in enumerate(tqdm(images, desc="OCR Progress"), 1):
        # Extract text with Hindi language
        text = pytesseract.image_to_string(
            image,
            lang='hin',  # Hindi language
            config=TESSERACT_CONFIG
        )
        
        extracted_pages.append({
            "text": text.strip(),
            "source_file": pdf_path,
            "grade": 6,
            "subject": "science",
            "language": "hindi",
            "page_num": page_num,
            "extraction_method": "ocr",
            "confidence": 1.0
        })
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_pages, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(extracted_pages)} pages to {output_path}")
    
    # Show sample
    if extracted_pages:
        print(f"\n📄 Sample from page 1:")
        print(extracted_pages[0]['text'][:300])


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    
    # Paths
    hindi_pdf = project_root / "data" / "raw" / "Vigyan.pdf"
    output_json = project_root / "data" / "processed" / "6_science_hindi_extracted_improved.json"
    
    if not hindi_pdf.exists():
        print(f"❌ Hindi PDF not found at: {hindi_pdf}")
        print("Please place the Hindi PDF (Vigyan.pdf) in data/raw/")
        exit(1)
    
    # Extract with improved settings
    extract_hindi_pdf_improved(
        pdf_path=str(hindi_pdf),
        output_path=str(output_json),
        dpi=300  # Higher DPI for better quality
    )
    
    print("\n" + "="*70)
    print("📝 NEXT STEPS:")
    print("="*70)
    print("\n1. Run chunking notebook (02_chunking_metadata.ipynb)")
    print("2. Run embedding notebook (03_embeddings_vectordb.ipynb)")
    print("   Make sure it uses: intfloat/multilingual-e5-large")
    print("3. Rebuild vector store:")
    print("   python scripts/rebuild_vector_store_multilingual.py")
    print("\n" + "="*70)