from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = None

def _get_client():
    global client
    if client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set. "
                "Please create a .env file with your GROQ_API_KEY."
            )
        client = Groq(api_key=api_key)
    return client

def generate_response(prompt):
    """
    Generate a response using Groq's LLM API.
    
    Model options:
    - llama-3.1-8b-instant (fast, reliable - currently used)
    - llama-3.3-70b-versatile (if available, high quality)
    - mixtral-8x7b-32768 (alternative option)
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Updated from deprecated llama-3.1-70b-versatile
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1200
    )
    return response.choices[0].message.content
