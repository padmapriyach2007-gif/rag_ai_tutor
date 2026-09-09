import os
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator

from dotenv import load_dotenv
from supabase import create_client, Client

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tavily import TavilyClient

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# =========================================================
# API KEYS
# =========================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

try:
    import streamlit as st
    if not GROQ_API_KEY:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    if not TAVILY_API_KEY:
        TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY")
    if not SUPABASE_URL:
        SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    if not SUPABASE_SERVICE_KEY:
        SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY")
except Exception:
    pass

# =========================================================
# VALIDATE SETTINGS
# =========================================================
missing_keys = []
if not GROQ_API_KEY: missing_keys.append("GROQ_API_KEY")
if not TAVILY_API_KEY: missing_keys.append("TAVILY_API_KEY")
if not SUPABASE_URL: missing_keys.append("SUPABASE_URL")
if not SUPABASE_SERVICE_KEY: missing_keys.append("SUPABASE_SERVICE_KEY")

if missing_keys:
    raise ValueError(
        "Missing required environment variables:\n"
        + "\n".join(f"- {key}" for key in missing_keys)
    )

# =========================================================
# CLIENTS
# =========================================================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# =========================================================
# EMBEDDING & LLM
# =========================================================
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings

def get_llm():
    # Upgraded to Llama-3.3-70b-versatile and enabled streaming
    return ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.5,
        api_key=GROQ_API_KEY,
        max_retries=3,
        request_timeout=60.0,
        streaming=True
    )

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# =========================================================
# USER / DB MANAGEMENT (Remains identical)
# =========================================================
def get_or_create_user(email: str, role: str = "student") -> str:
    email = email.strip().lower()
    response = supabase.table("users").select("user_id").eq("email", email).limit(1).execute()
    if response.data: return response.data[0]["user_id"]
    response = supabase.table("users").insert({"email": email, "role": role}).execute()
    return response.data[0]["user_id"]

def create_chat_session(user_id: str, title: str = "New Quantum Chat") -> str:
    response = supabase.table("chat_sessions").insert({"user_id": user_id, "title": title}).execute()
    return response.data[0]["session_id"]

def get_user_sessions(user_id: str):
    response = supabase.table("chat_sessions").select("session_id, title, created_at").eq("user_id", user_id).order("created_at", desc=True).execute()
    return response.data or []

def verify_session_owner(session_id: str, user_id: str) -> bool:
    response = supabase.table("chat_sessions").select("session_id").eq("session_id", session_id).eq("user_id", user_id).limit(1).execute()
    return bool(response.data)

def rename_chat(session_id: str, user_id: str, new_title: str):
    if not verify_session_owner(session_id, user_id): raise PermissionError("Permission denied.")
    return supabase.table("chat_sessions").update({"title": new_title.strip()}).eq("session_id", session_id).execute().data

def save_message(session_id: str, sender: str, content: str):
    if content:
        supabase.table("chat_messages").insert({"session_id": session_id, "sender": sender, "content": content}).execute()

def get_chat_history(session_id: str):
    response = supabase.table("chat_messages").select("message_id, sender, content, created_at").eq("session_id", session_id).order("created_at", desc=False).execute()
    return response.data or []

def restore_chat(session_id: str, user_id: str):
    if not verify_session_owner(session_id, user_id): raise PermissionError("Permission denied.")
    return get_chat_history(session_id)

def delete_chat(session_id: str, user_id: str):
    if not verify_session_owner(session_id, user_id): raise PermissionError("Permission denied.")
    supabase.table("chat_sessions").delete().eq("session_id", session_id).execute()

def clear_chat(session_id: str, user_id: str):
    if not verify_session_owner(session_id, user_id): raise PermissionError("Permission denied.")
    supabase.table("chat_messages").delete().eq("session_id", session_id).execute()

def format_history(history) -> str:
    return "\n".join([f"{'User' if m['sender']=='user' else 'Assistant'}: {m['content']}" for m in history if m.get('content')])

# =========================================================
# FILE PARSING (Remains identical)
# =========================================================
def read_text_file(fp: Path) -> str: return fp.read_text(encoding="utf-8", errors="ignore")
def read_pdf_file(fp: Path) -> str:
    try:
        from pypdf import PdfReader
        return "\n\n".join([p.extract_text() for p in PdfReader(str(fp)).pages if p.extract_text()])
    except: return ""
def read_docx_file(fp: Path) -> str:
    try:
        from docx import Document
        return "\n\n".join([p.text for p in Document(str(fp)).paragraphs if p.text.strip()])
    except: return ""
def read_csv_file(fp: Path) -> str:
    try:
        import csv
        with open(fp, "r", encoding="utf-8", errors="ignore", newline="") as f:
            return "\n".join([" | ".join(row) for row in csv.reader(f)])
    except: return ""

def load_file(fp: Path) -> str:
    ext = fp.suffix.lower()
    if ext in [".txt", ".md", ".py", ".c", ".cpp", ".java", ".js", ".html", ".css", ".sql"]: return read_text_file(fp)
    if ext == ".pdf": return read_pdf_file(fp)
    if ext == ".docx": return read_docx_file(fp)
    if ext == ".csv": return read_csv_file(fp)
    return ""

def get_file_hash(fp: Path) -> str:
    sha256 = hashlib.sha256()
    with open(fp, "rb") as f:
        while True:
            data = f.read(1024 * 1024)
            if not data: break
            sha256.update(data)
    return sha256.hexdigest()

def get_existing_document_hashes() -> set:
    response = supabase.table("documents").select("metadata").execute()
    return {r.get("metadata", {}).get("file_hash") for r in (response.data or []) if r.get("metadata", {}).get("file_hash")}

def ingest_documents(documents_dir: str = "documents") -> int:
    docs_path = BASE_DIR / documents_dir
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)
        return 0
    files = [f for f in docs_path.rglob("*") if f.is_file() and f.suffix.lower() in {".pdf", ".txt", ".md", ".docx", ".csv", ".py", ".c", ".cpp", ".java", ".js", ".html", ".css", ".sql"}]
    existing_hashes = get_existing_document_hashes()
    embeddings = get_embeddings()
    inserted = 0

    for fp in files:
        f_hash = get_file_hash(fp)
        if f_hash in existing_hashes: continue
        text = load_file(fp)
        if not text.strip(): continue
        chunks = text_splitter.split_text(text)
        if not chunks: continue
        vectors = embeddings.embed_documents(chunks)
        rows = [{"content": c, "embedding": v, "metadata": {"source": fp.name, "path": str(fp), "chunk_index": i, "file_hash": f_hash}} for i, (c, v) in enumerate(zip(chunks, vectors))]
        
        for start in range(0, len(rows), 50):
            supabase.table("documents").insert(rows[start:start+50]).execute()
        existing_hashes.add(f_hash)
        inserted += 1
    return inserted

def retrieve_documents(query: str, match_count: int = 5) -> List[Dict[str, Any]]:
    query_embedding = get_embeddings().embed_query(query)
    response = supabase.rpc("match_documents", {"query_embedding": query_embedding, "match_count": match_count}).execute()
    return response.data or []

def format_rag_context(documents: List[Dict[str, Any]]) -> str:
    return "\n".join([f"-- Source: {d.get('metadata', {}).get('source', 'DB')} --\n{d.get('content', '')}" for d in documents])

def web_search(query: str) -> str:
    try:
        results = tavily_client.search(query=query, search_depth="advanced", max_results=3)
        return "\n\n".join([f"Title: {r.get('title')}\nURL: {r.get('url')}\nInfo: {r.get('content')}" for r in results.get("results", [])])
    except: return ""

def needs_web_search(query: str) -> bool:
    q_lower = query.lower().strip()
    if len(q_lower.split()) <= 3 and not q_lower.startswith(("what is", "how to", "explain")): return True
    keywords = ["latest", "current", "today", "news", "2026", "2025", "price", "weather", "stock", "release"]
    return any(k in q_lower for k in keywords)

# =========================================================
# GENERATE ANSWER (STREAMING)
# =========================================================
def generate_answer_stream(query: str, history: str = "", rag_context: str = "", web_context: str = "") -> Generator:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are Quantum Lab's RAG AI Tutor.
IMPORTANT RAG RULES:
1. Answer the exact question asked.
2. Use KNOWLEDGE BASE CONTEXT primarily.
3. If retrieved knowledge is insufficient, use general knowledge.
4. WEB CONTEXT is for current/time-sensitive questions.
5. Do not mention internal processes, databases, or API keys.

PREVIOUS CONVERSATION:
{history}

KNOWLEDGE BASE CONTEXT:
{rag_context}

WEB CONTEXT:
{web_context}
"""),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.stream({
        "history": history,
        "rag_context": rag_context,
        "web_context": web_context,
        "input": query
    })

def answer_question_stream(query: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> Generator:
    query = query.strip()
    if not query:
        yield "Please enter a question."
        return

    if session_id and user_id and not verify_session_owner(session_id, user_id):
        raise PermissionError("Access denied.")

    history_str = ""
    if session_id:
        history = get_chat_history(session_id)
        history_str = format_history(history[-10:])
        save_message(session_id, "user", query)

    rag_documents = retrieve_documents(query, match_count=5)
    rag_context = format_rag_context(rag_documents)
    web_context = web_search(query) if needs_web_search(query) else ""

    stream = generate_answer_stream(query, history_str, rag_context, web_context)
    
    full_response = ""
    for chunk in stream:
        full_response += chunk
        yield chunk

    if session_id:
        save_message(session_id, "assistant", full_response)

def initialize_knowledge_base():
    return ingest_documents(documents_dir="documents")
