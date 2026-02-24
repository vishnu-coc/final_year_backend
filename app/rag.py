import faiss
import pickle
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Get the project root directory (parent of 'app' directory)
BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "faiss_index" / "index.faiss"
TEXT_PATH = BASE_DIR / "faiss_index" / "texts.pkl"
BM25_PATH = BASE_DIR / "faiss_index" / "bm25_index.pkl"

model = None
index = None
bm25 = None
texts = None

def _load_index():
    global model, index, bm25, texts
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    
    if index is None or texts is None or bm25 is None:
        if not INDEX_PATH.exists() or not TEXT_PATH.exists() or not BM25_PATH.exists():
            raise FileNotFoundError(
                f"Index files not found. Please run 'python app/ingest.py' first to create the index."
            )
        index = faiss.read_index(str(INDEX_PATH))
        with open(TEXT_PATH, "rb") as f:
            texts = pickle.load(f)
        with open(BM25_PATH, "rb") as f:
            bm25 = pickle.load(f)

def retrieve_legal_context(query, top_k=5):
    """
    Hybrid retrieval using Dense (FAISS) and Sparse (BM25) search
    with Reciprocal Rank Fusion (RRF).
    """
    _load_index()
    
    # 1. Dense Retrieval (FAISS)
    query_embedding = model.encode([query])
    distances, dense_indices = index.search(query_embedding, top_k)
    dense_results = dense_indices[0]
    
    # 2. Sparse Retrieval (BM25)
    tokenized_query = query.split()
    sparse_scores = bm25.get_scores(tokenized_query)
    # Get indices of top_k scores
    sparse_results = sorted(range(len(sparse_scores)), key=lambda i: sparse_scores[i], reverse=True)[:top_k]
    
    # 3. Reciprocal Rank Fusion (RRF)
    k = 60 # Constant for RRF
    rrf_scores = {}
    
    # Rank from 0 to top_k-1 (so rank 0 is best)
    for rank, idx in enumerate(dense_results):
        if idx not in rrf_scores: rrf_scores[idx] = 0
        rrf_scores[idx] += 1 / (k + rank + 1)
        
    for rank, idx in enumerate(sparse_results):
        if idx not in rrf_scores: rrf_scores[idx] = 0
        rrf_scores[idx] += 1 / (k + rank + 1)
    
    # Sort by RRF score
    sorted_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    # Return top_k unique results
    final_indices = sorted_indices[:top_k]
    
    return [texts[i] for i in final_indices]
