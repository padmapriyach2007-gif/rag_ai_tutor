import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tavily import TavilyClient

# Environment Setup
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

try:
    import streamlit as st
    if not GROQ_API_KEY: GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    if not TAVILY_API_KEY: TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY")
    if not SUPABASE_URL: SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    if not SUPABASE_SERVICE_KEY: SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY")
except Exception:
    pass

# Initialize LLM
def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.5,
        api_key=GROQ_API_KEY,
        max_retries=3,
        request_timeout=60.0
    )

# Web Search Engine
def web_search(query: str) -> str:
    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        results = tavily.search(query=query, search_depth="advanced", max_results=5)
        web_context = []
        for result in results.get("results", []):
            if result.get("content"):
                web_context.append(f"Title: {result.get('title')}\nSource: {result.get('url')}\nInfo: {result.get('content')}")
        return "\n\n".join(web_context)
    except Exception as e:
        print("Tavily Search Error:", e)
        return ""

def needs_web_search(query: str) -> bool:
    query_lower = query.lower().strip()
    if len(query_lower.split()) <= 3 and not query_lower.startswith(("what is", "how to", "explain")):
        return True
    keywords = ["latest", "current", "today", "now", "recent", "2026", "news", "price", "weather"]
    return any(k in query_lower for k in keywords)

# Core Answer Function required by app.py
def answer_question(query: str, session_id: str = None, user_id: str = None) -> str:
    query = query.strip()
    if not query:
        return "Please enter a valid question."

    web_context = ""
    if needs_web_search(query):
        web_context = web_search(query)

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an intelligent, versatile, and helpful AI Assistant.
Answer any question asked by the user clearly, completely, and accurately.
If Web Context is provided, use it to ensure your response is accurate and up to date.

WEB CONTEXT:
{web_context}
"""),
        ("human", "{input}")
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        return chain.invoke({"web_context": web_context, "input": query})
    except Exception as e:
        return f"Sorry, I could not generate a response right now.\n\nError: {str(e)}"
