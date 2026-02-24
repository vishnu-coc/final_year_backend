import os
import pdfplumber
import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import json

# Get the project root directory (parent of 'app' directory)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "legal_docs"
INDEX_DIR = BASE_DIR / "faiss_index"

model = SentenceTransformer("all-MiniLM-L6-v2")

def ingest_documents():
    texts = []

    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {DATA_DIR}")
        return

    if not DATA_DIR.is_dir():
        raise ValueError(f"{DATA_DIR} exists but is not a directory")

    supported_files = [f for f in os.listdir(str(DATA_DIR)) if f.endswith(".pdf") or f.endswith(".txt") or f.endswith(".json")]
    
    if not supported_files:
        print(f"No PDF, TXT, or JSON files found in {DATA_DIR}")
        print(f"Please add files to {DATA_DIR} and run this script again.")
        return

    print(f"Found {len(supported_files)} file(s). Processing...")
    
    for file in supported_files:
        file_path = DATA_DIR / file
        print(f"Processing: {file}")
        try:
            text = ""
            if file.endswith(".pdf"):
                with pdfplumber.open(str(file_path)) as pdf:
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                
                if text:
                    texts.append({
                        "content": text,
                        "metadata": {
                            "source": file,
                            "type": "pdf" 
                        }
                    })

            elif file.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                if text:
                    texts.append({
                        "content": text,
                        "metadata": {
                            "source": file,
                            "type": "txt"
                        }
                    })

            elif file.endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    for item in data:
                        if "question" in item and "answer" in item:
                            qa_text = f"Question: {item['question']}\nAnswer: {item['answer']}"
                            texts.append({
                                "content": qa_text,
                                "metadata": {
                                    "source": file,
                                    "type": "json_qa"
                                }
                            })
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

    if not texts:
        print("No text extracted from PDF files. Please check your PDF files.")
        return

    print(f"Extracted {len(texts)} text chunks. Creating embeddings...")
    # Extract just the text content for embedding
    text_contents = [t["content"] for t in texts]
    embeddings = model.encode(text_contents)
    print(f"Created embeddings with shape: {embeddings.shape}")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))

    # Create and save BM25 index
    print("Creating BM25 sparse index...")
    from rank_bm25 import BM25Okapi
    tokenized_corpus = [doc.split() for doc in text_contents]
    bm25 = BM25Okapi(tokenized_corpus)
    
    with open(INDEX_DIR / "bm25_index.pkl", "wb") as f:
        pickle.dump(bm25, f)

    with open(INDEX_DIR / "texts.pkl", "wb") as f:
        pickle.dump(texts, f)

    print(f"Ingestion completed. Index saved to {INDEX_DIR}/")
    print(f"Total documents indexed: {len(texts)}")

if __name__ == "__main__":
    ingest_documents()
