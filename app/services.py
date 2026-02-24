from app.rag import retrieve_legal_context
from app.llm import generate_response
from app.prompts import legal_prompt
from typing import List, Dict, Any

class QueryProcessingService:
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Orchestrates the retrieval and generation process for a user query.
        """
        # 1. Retrieval
        try:
            context_chunks = retrieve_legal_context(query)
        except FileNotFoundError as e:
            # Re-raise or handle specific errors
            raise e

        context_texts = []
        sources = []

        # 2. Preprocessing / Formatting
        for chunk in context_chunks:
            if isinstance(chunk, dict) and "content" in chunk:
                context_texts.append(chunk["content"])
                sources.append(chunk["metadata"])
            else:
                context_texts.append(str(chunk))

        combined_context = "\n".join(context_texts)

        # 3. Augmentation (Context Building)
        prompt = legal_prompt(combined_context, query)

        # 4. Generation
        answer = generate_response(prompt)

        return {
            "question": query,
            "answer": answer,
            "sources": sources
        }
