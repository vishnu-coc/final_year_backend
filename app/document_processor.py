import pdfplumber
import io
from typing import List, Dict, Any

def extract_text_from_pdf(file_content: bytes) -> Dict[str, Any]:
    """
    Extract text from PDF file content.
    
    Args:
        file_content: PDF file content as bytes
        
    Returns:
        Dictionary containing extracted text, page count, and metadata
    """
    try:
        text_chunks = []
        total_pages = 0
        pages_with_text = 0
        pages_without_text = []
        
        # Open PDF from bytes
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            total_pages = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Try multiple extraction methods
                text = page.extract_text()
                
                # Try alternative method if first fails
                if not text or not text.strip():
                    # Try extracting with layout preservation
                    try:
                        text = page.extract_text(layout=True)
                    except:
                        pass
                
                # Try extracting tables as text if still no text
                if not text or not text.strip():
                    try:
                        tables = page.extract_tables()
                        if tables:
                            table_texts = []
                            for table in tables:
                                for row in table:
                                    if row:
                                        row_text = " | ".join([str(cell) if cell else "" for cell in row])
                                        table_texts.append(row_text)
                            if table_texts:
                                text = "\n".join(table_texts)
                    except:
                        pass
                
                if text and text.strip():
                    text_chunks.append({
                        "page": page_num,
                        "text": text.strip()
                    })
                    pages_with_text += 1
                else:
                    pages_without_text.append(page_num)
        
        full_text = "\n\n".join([chunk["text"] for chunk in text_chunks])
        
        # Determine if PDF is likely image-based
        is_image_based = total_pages > 0 and pages_with_text == 0
        
        return {
            "success": True,
            "total_pages": total_pages,
            "pages_with_text": pages_with_text,
            "pages_without_text": pages_without_text,
            "is_image_based": is_image_based,
            "text_chunks": text_chunks,
            "full_text": full_text,
            "text_length": len(full_text),
            "chunks_count": len(text_chunks)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_pages": 0,
            "pages_with_text": 0,
            "pages_without_text": [],
            "is_image_based": False,
            "text_chunks": [],
            "full_text": "",
            "text_length": 0,
            "chunks_count": 0
        }

def analyze_document_structure(text: str) -> Dict[str, Any]:
    """
    Analyze document structure and provide basic statistics.
    
    Args:
        text: Extracted text from document
        
    Returns:
        Dictionary with document analysis metrics
    """
    words = text.split()
    sentences = text.split('.')
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    return {
        "total_characters": len(text),
        "total_words": len(words),
        "total_sentences": len([s for s in sentences if s.strip()]),
        "total_paragraphs": len(paragraphs),
        "average_words_per_sentence": len(words) / max(len([s for s in sentences if s.strip()]), 1),
        "estimated_reading_time_minutes": round(len(words) / 200, 2)  # Average reading speed: 200 words/min
    }
