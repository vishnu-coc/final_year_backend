from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.prompts import extract_key_points_prompt, analyze_key_points_prompt
from app.llm import generate_response
from app.document_processor import extract_text_from_pdf, analyze_document_structure
from app.services import QueryProcessingService
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fastapi.middleware.cors import CORSMiddleware

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AI Legal Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize services
query_service = QueryProcessingService()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
@limiter.limit("5/minute")
async def ask_question(request: Request, question_request: QuestionRequest):
    try:
        response = await query_service.process_query(question_request.question)
        return response
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze_document(
    request: Request,
    file: UploadFile = File(..., description="PDF document to analyze"),
    question: Optional[str] = Form(None, description="Optional question about the document")
):
    """
    Analyze a PDF document and provide analysis or answer questions about it.
    
    - **file**: PDF file to upload and analyze
    - **question**: (Optional) Specific question about the document
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported. Please upload a PDF file."
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF
        extraction_result = extract_text_from_pdf(file_content)
        
        if not extraction_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from PDF: {extraction_result.get('error', 'Unknown error')}"
            )
        
        if not extraction_result["full_text"]:
            # Provide detailed error message
            total_pages = extraction_result.get("total_pages", 0)
            is_image_based = extraction_result.get("is_image_based", False)
            
            if is_image_based and total_pages > 0:
                detail = (
                    f"No text could be extracted from the PDF. The PDF appears to be image-based (scanned document) "
                    f"with {total_pages} page(s). "
                    f"This API currently supports text-based PDFs only. "
                    f"Please use a PDF with selectable text, or convert your scanned PDF to text using OCR software first."
                )
            elif total_pages == 0:
                detail = (
                    "The PDF file appears to be empty or corrupted. "
                    "Please verify the file is a valid PDF document."
                )
            else:
                detail = (
                    f"No text could be extracted from the PDF ({total_pages} page(s) processed). "
                    f"Possible reasons: "
                    f"1) The PDF contains only images/scans (needs OCR), "
                    f"2) The PDF is password-protected, "
                    f"3) The PDF is corrupted, or "
                    f"4) The PDF has no text content. "
                    f"Please use a PDF with selectable text."
                )
            
            raise HTTPException(
                status_code=400,
                detail=detail
            )
        
        # Analyze document structure
        document_stats = analyze_document_structure(extraction_result["full_text"])
        
        # Step 1: Extract key points from the document using Groq API
        key_points_prompt = extract_key_points_prompt(extraction_result["full_text"])
        key_points = generate_response(key_points_prompt)
        
        # Step 2: Analyze the extracted key points using Groq API
        analysis_prompt = analyze_key_points_prompt(key_points, question)
        ai_analysis = generate_response(analysis_prompt)
        
        # Prepare response
        response = {
            "filename": file.filename,
            "document_stats": {
                "total_pages": extraction_result["total_pages"],
                "total_characters": document_stats["total_characters"],
                "total_words": document_stats["total_words"],
                "total_sentences": document_stats["total_sentences"],
                "total_paragraphs": document_stats["total_paragraphs"],
                "estimated_reading_time_minutes": document_stats["estimated_reading_time_minutes"]
            },
            "key_points": key_points,
            "question": question,
            "analysis": ai_analysis,
            "extraction_summary": {
                "text_chunks_extracted": extraction_result["chunks_count"],
                "text_length": extraction_result["text_length"]
            }
        }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing document: {str(e)}"
        )
