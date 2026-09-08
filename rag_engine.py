import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# HuggingFace for Local Embeddings
from sentence_transformers import SentenceTransformer

# Vector Database Client
from supabase import create_client, Client

# Web Search Fallback
from duckduckgo_search import DDGS

# LLM Client
from groq import Groq

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Environment Configurations
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model Configuration Settings
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Global Singletons
_embedding_model: Optional[SentenceTransformer] = None
_supabase_client: Optional[Client] = None
_groq_client: Optional[Groq] = None


def get_embedding_model() -> SentenceTransformer:
    """Lazy initialization for the local SentenceTransformer embedding model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def get_supabase_client() -> Client:
    """Lazy initialization for the Supabase vector store client."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required.")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def get_groq_client() -> Groq:
    """Lazy initialization for the Groq API client."""
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required.")
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


def call_groq_llm(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> str:
    """Executes an API request to Groq with automatic model fallback logic."""
    client = get_groq_client()
    
    try:
        response = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Primary model {PRIMARY_MODEL} failed: {e}. Attempting fallback to {FALLBACK_MODEL}...")
        try:
            response = client.chat.completions.create(
                model=FALLBACK_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as fallback_err:
            logger.error(f"Fallback model {FALLBACK_MODEL} also failed: {fallback_err}")
            raise RuntimeError(f"All LLM generation attempts failed: {fallback_err}")


def generate_embedding(text: str) -> List[float]:
    """Generates a dense vector embedding for a given string."""
    model = get_embedding_model()
    embeddings = model.encode(text)
    return embeddings.tolist()


def rewrite_query(query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Rewrites ambiguous user questions into standalone queries based on chat context.
    """
    if not chat_history:
        return query

    context_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history[-4:]])
    
    system_prompt = (
        "You are an expert NLP assistant. Given a user question and conversation context, "
        "rephrase the question into a fully standalone search query. "
        "Keep the revised question concise and focused on intent. Return ONLY the rewritten question string."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}\nRewritten Question:"}
    ]
    
    try:
        rewritten = call_groq_llm(messages, temperature=0.1, max_tokens=100)
        logger.info(f"Original Query: '{query}' -> Rewritten: '{rewritten}'")
        return rewritten
    except Exception:
        return query


def retrieve_documents(query: str, match_threshold: float = 0.45, match_count: int = 5) -> List[Dict[str, Any]]:
    """Retrieves similar document chunks from the Supabase PGVector store."""
    try:
        supabase = get_supabase_client()
        query_vector = generate_embedding(query)
        
        rpc_params = {
            'query_embedding': query_vector,
            'match_threshold': match_threshold,
            'match_count': match_count
        }
        
        response = supabase.rpc('match_documents', rpc_params).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error executing vector database query: {e}")
        return []


def perform_web_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Performs a live web search fallback when database context is insufficient."""
    logger.info(f"Triggering web search fallback for query: '{query}'")
    results = []
    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=max_results))
            for res in search_results:
                results.append({
                    "title": res.get("title", "Web Result"),
                    "snippet": res.get("body", ""),
                    "url": res.get("href", "")
                })
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
    return results


def log_interaction_to_supabase(
    query: str,
    response: str,
    sources: List[Dict[str, Any]],
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """Logs the interaction session to the Supabase database for audit trails and UI history."""
    try:
        supabase = get_supabase_client()
        record = {
            "query": query,
            "response": response,
            "sources": json.dumps(sources),
            "session_id": session_id,
            "user_id": user_id
        }
        supabase.table("chat_logs").insert(record).execute()
    except Exception as e:
        logger.warning(f"Failed to persist chat log record: {e}")


def answer_question(
    query: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    match_threshold: float = 0.45
) -> Dict[str, Any]:
    """
    Main execution pipeline for handling user queries.
    Applies Query Rewriting -> Vector Search -> Web Fallback (if needed) -> Response Generation -> Logging.
    """
    # Step 1: Query Enhancement
    effective_query = rewrite_query(query, chat_history) if chat_history else query

    # Step 2: Retrieve context from Supabase Vector Store
    docs = retrieve_documents(effective_query, match_threshold=match_threshold, match_count=5)
    
    source_type = "vector_db"
    used_sources = []
    
    # Step 3: Handle Fallback if Vector DB returns empty or weak matches
    if not docs:
        source_type = "web_search"
        web_results = perform_web_search(effective_query)
        context_blocks = [f"Title: {res['title']}\nContent: {res['snippet']}" for res in web_results]
        context_str = "\n\n---\n\n".join(context_blocks) if context_blocks else "No relevant context found."
        used_sources = web_results
    else:
        context_blocks = [f"Document Chunk:\n{doc.get('content', '')}" for doc in docs]
        context_str = "\n\n---\n\n".join(context_blocks)
        used_sources = [{"id": doc.get("id"), "content": doc.get("content"), "metadata": doc.get("metadata")} for doc in docs]

    # Step 4: Construct System & Generation Prompt
    system_instruction = (
        "You are an expert AI Assistant designed to answer user questions accurately, concisely, and helpfully.\n"
        "Instructions:\n"
        "1. Base your answer on the provided Context whenever relevant.\n"
        "2. If the context does not contain enough information, use your internal general knowledge to fulfill the request completely and correctly.\n"
        "3. Provide clean code snippets when asked for code solutions.\n"
        "4. Be polite, direct, and authoritative in standard analytical tone."
    )

    prompt_messages = [{"role": "system", "content": system_instruction}]

    # Append Conversation History if present
    if chat_history:
        for turn in chat_history[-6:]:
            prompt_messages.append({"role": turn["role"], "content": turn["content"]})

    # Append final augmented request
    final_user_prompt = f"Context Information:\n{context_str}\n\nUser Question: {query}"
    prompt_messages.append({"role": "user", "content": final_user_prompt})

    # Step 5: Generate LLM Response
    response_text = call_groq_llm(prompt_messages)

    # Step 6: Log Session Activity
    log_interaction_to_supabase(
        query=query,
        response=response_text,
        sources=used_sources,
        session_id=session_id,
        user_id=user_id
    )

    return {
        "query": query,
        "effective_query": effective_query,
        "response": response_text,
        "source_type": source_type,
        "sources": used_sources
    }


if __name__ == "__main__":
    # Internal Unit Execution Test
    test_query = "What is quantum superposition?"
    print(f"Testing execution flow with query: '{test_query}'\n")
    output = answer_question(test_query)
    print("--- RESPONSE ---")
    print(output["response"])
    print("\n--- METADATA ---")
    print(f"Source Type Used: {output['source_type']}")
