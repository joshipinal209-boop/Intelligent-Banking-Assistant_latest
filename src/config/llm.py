import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    """
    Initializes and returns a ChatGoogleGenerativeAI client.
    
    Loads configuration from environment variables:
    - GOOGLE_API_KEY: Required.
    - GEMINI_MODEL: Defaults to 'gemini-2.0-flash' if not set.
    
    Returns:
        ChatGoogleGenerativeAI: A ready LLM instance.
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not found in the environment.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable. Please check your .env file.")
        
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.2,
        max_output_tokens=2048,
    )
    
    return llm
