import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

try:
    import streamlit as st
    if not GROQ_API_KEY:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    if not TAVILY_API_KEY:
        TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY")
except Exception:
    pass


def web_search(query: str) -> str:
    """Performs live web search using Tavily."""
    if not TAVILY_API_KEY:
        return ""
    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        results = tavily.search(query=query, search_depth="basic", max_results=4)
        web_context = []
        for result in results.get("results", []):
            if result.get("content"):
                web_context.append(
                    f"Title: {result.get('title')}\n"
                    f"Source: {result.get('url')}\n"
                    f"Info: {result.get('content')}"
                )
        return "\n\n".join(web_context)
    except Exception as e:
        print("Tavily Search Error:", e)
        return ""


def needs_web_search(query: str) -> bool:
    """Determines if a query requires external web search context."""
    query_lower = query.lower().strip()
    
    # Simple general prompts like "what is c" or short terms
    if len(query_lower.split()) <= 3 and not query_lower.startswith(("what is", "how to", "explain")):
        return True
        
    keywords = [
        "latest", "current", "today", "now", "recent", "2026", "2025",
        "news", "price", "weather", "who is", "movie", "release"
    ]
    return any(k in query_lower for k in keywords)


def answer_question(query: str, session_id: str = None, user_id: str = None) -> str:
    """
    Core function called by app.py.
    Uses native Groq SDK to prevent Hugging Face / OpenAI 403 authorization errors.
    """
    query = query.strip()
    if not query:
        return "Please enter a valid question."

    if not GROQ_API_KEY:
        return "Error: `GROQ_API_KEY` is missing. Please add it to your `.env` file."

    # Perform web search if required
    web_context = ""
    if needs_web_search(query):
        web_context = web_search(query)

    # Initialize native Groq client
    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = (
        "You are an intelligent, versatile, and helpful AI Assistant.\n"
        "Answer any question asked by the user clearly, completely, and accurately.\n"
        "If Web Context is provided, use it to ensure your response is up to date.\n\n"
        f"WEB CONTEXT:\n{web_context}"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.5,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I could not generate a response right now.\n\nError details: {str(e)}"
