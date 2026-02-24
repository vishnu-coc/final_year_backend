def legal_prompt(context, question):
    return f"""
You are an AI legal assistant.
Answer the following question using the legal context provided.

INSTRUCTIONS:
1. Provide a DETAILED and COMPREHENSIVE answer.
2. Explain the relevant legal sections (e.g., IPC sections) found in the context.
3. Apply the law to the specific question or case scenario provided.
4. If there are multiple relevant sections or points, structure your answer clearly (e.g., using bullet points).
5. Explain the implications of the law (e.g., punishment, definitions).

If the answer is NOT found in the legal context, you may answer using your general knowledge, but you MUST assume the role of a standard legal assistant and add the following disclaimer at the start:
"**Disclaimer: This answer is based on general legal principles and not found in your indexed documents.**"

LEGAL CONTEXT:
{context}

QUESTION:
{question}

NOTE:
This is not legal advice.
"""

def extract_key_points_prompt(document_text: str) -> str:
    """
    Generate a prompt to extract key points from the document.
    """
    return f"""
You are an AI document analysis assistant. Extract and list the key points from the following document.

DOCUMENT CONTENT:
{document_text}

INSTRUCTIONS:
- Identify and extract all the key points, main ideas, and important information from the document
- Organize the key points in a clear, structured format
- Use bullet points or numbered list
- Be comprehensive but concise
- Focus on the most important and relevant information
- Include any critical facts, figures, dates, names, or concepts mentioned

Return ONLY the key points extracted from the document, formatted clearly.
"""

def analyze_key_points_prompt(key_points: str, question: str = None) -> str:
    """
    Generate a prompt to analyze extracted key points.
    If question is provided, answer it based on the key points.
    Otherwise, provide a comprehensive analysis.
    """
    if question:
        return f"""
You are an AI analysis assistant. Analyze the following key points extracted from a document and answer the question.

KEY POINTS FROM DOCUMENT:
{key_points}

QUESTION:
{question}

INSTRUCTIONS:
- Analyze the key points and provide a detailed answer to the question
- Use ONLY the information from the key points provided
- Be specific and detailed in your answer
- If the answer cannot be found in the key points, state that clearly
- Provide a comprehensive and well-structured answer
"""
    else:
        return f"""
You are an AI analysis assistant. Analyze and provide insights about the following key points extracted from a document.

KEY POINTS FROM DOCUMENT:
{key_points}

INSTRUCTIONS:
- Provide a comprehensive analysis and insights about these key points
- Identify connections, patterns, and relationships between the points
- Highlight the most significant insights or implications
- Provide context and interpretation of the key points
- Structure your analysis clearly with sections or bullet points
- Be thorough and analytical in your response
"""