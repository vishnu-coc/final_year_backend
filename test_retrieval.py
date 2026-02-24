import sys
import os
from pathlib import Path

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag import retrieve_legal_context

def test_retrieval():
    query = "What is the penalty for murder?"
    print(f"Query: {query}")
    try:
        results = retrieve_legal_context(query)
        print(f"Retrieved {len(results)} chunks.")
        for i, res in enumerate(results):
            print(f"--- Chunk {i+1} ---")
            print(res['content'][:200] + "...")
            print(f"Source: {res['metadata']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_retrieval()
