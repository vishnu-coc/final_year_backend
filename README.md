# AI Legal Assistant Backend

This project implements a Transformer-based AI Legal Assistant backend using FastAPI and Retrieval-Augmented Generation (RAG). The system ingests legal PDF documents, extracts and chunks their content, and indexes them using vector embeddings stored in FAISS. It integrates with the Groq API running LLaMA 3.1 to generate grounded legal responses. The backend supports two primary workflows: document-specific analysis via a `/analyze` endpoint and knowledge-base querying via a `/ask` endpoint, ensuring accurate, context-aware, and legally grounded AI assistance.

## Key Features

*   **RAG-based Question Answering**: Query your private legal documents.
*   **Document Analysis**: Upload a PDF to get an instant summary, key points, and analysis.
*   **Citations & Sources**: Answers include references to the specific file and page number.
*   **Hallucination Control**: Explicitly handles cases where information is not found.
*   **Scanned PDF Detection**: Rejects image-based PDFs with clear error messages.
*   **Rate Limiting**: Protects the API from abuse (default: 5 requests/minute).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file with your Groq API key:
    ```
    GROQ_API_KEY=your_api_key_here
    ```

3.  **Ingest Documents**:
    Place your PDF files in `data/legal_docs/` and run:
    ```bash
    python -m app.ingest
    ```
    *Note: You must run ingestion to build the vector index. The system detects metadata (page numbers) during this step.*

4.  **Run the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```

## API Usage

### `/ask` (RAG Query)
*   **Method**: `POST`
*   **Body**: `{"question": "What is the termination notice period?"}`
*   **Response**:
    ```json
    {
      "question": "What is the termination notice period?",
      "answer": "The termination notice period is 30 days...",
      "sources": [
        {"source": "contract.pdf", "page": 5},
        {"source": "agreement.pdf", "page": 2}
      ]
    }
    ```

### `/analyze` (Single Doc Analysis)
*   **Method**: `POST`
*   **Form Data**: `file` (PDF), `question` (Optional text)
