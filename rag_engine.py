import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from tavily import TavilyClient

from ingest import build_vector_db


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

HF_TOKEN = os.getenv("HF_TOKEN")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


# =========================================================
# STREAMLIT SECRETS FALLBACK
# =========================================================

try:
    import streamlit as st

    if not HF_TOKEN:
        HF_TOKEN = st.secrets.get("HF_TOKEN")

    if not TAVILY_API_KEY:
        TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY")

    if not SUPABASE_URL:
        SUPABASE_URL = st.secrets.get("SUPABASE_URL")

    if not SUPABASE_SERVICE_KEY:
        SUPABASE_SERVICE_KEY = st.secrets.get(
            "SUPABASE_SERVICE_KEY"
        )

except Exception:
    pass


# =========================================================
# VALIDATE API KEYS
# =========================================================

if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN is missing. "
        "Add it to .env or Streamlit Secrets."
    )

if not TAVILY_API_KEY:
    raise ValueError(
        "TAVILY_API_KEY is missing. "
        "Add it to .env or Streamlit Secrets."
    )

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing. "
        "Add it to .env or Streamlit Secrets."
    )

if not SUPABASE_SERVICE_KEY:
    raise ValueError(
        "SUPABASE_SERVICE_KEY is missing. "
        "Add it to .env or Streamlit Secrets."
    )


# =========================================================
# SUPABASE CONNECTION
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)


# =========================================================
# TAVILY CONNECTION
# =========================================================

tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


# =========================================================
# LLM
# =========================================================

def get_llm():

    return ChatOpenAI(
        model="openai/gpt-oss-120b",
        temperature=0.4,
        api_key=HF_TOKEN,
        base_url="https://router.huggingface.co/v1"
    )


# =========================================================
# EMBEDDINGS
# =========================================================

def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )


# =========================================================
# USER MANAGEMENT
# =========================================================

def get_or_create_user(
    email: str,
    role: str = "student"
) -> str:

    email = email.strip().lower()

    # Check existing user
    response = (
        supabase
        .table("users")
        .select("user_id")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]["user_id"]

    # Create new user
    response = (
        supabase
        .table("users")
        .insert({
            "email": email,
            "role": role
        })
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Failed to create user."
        )

    return response.data[0]["user_id"]


# =========================================================
# CREATE CHAT SESSION
# =========================================================

def create_chat_session(
    user_id: str,
    title: str = "New AI Tutor Chat"
) -> str:

    response = (
        supabase
        .table("chat_sessions")
        .insert({
            "user_id": user_id,
            "title": title
        })
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Failed to create chat session."
        )

    return response.data[0]["session_id"]


# =========================================================
# GET USER SESSIONS
# =========================================================

def get_user_sessions(user_id: str):

    response = (
        supabase
        .table("chat_sessions")
        .select(
            "session_id, title, created_at"
        )
        .eq(
            "user_id",
            user_id
        )
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )

    return response.data or []


# =========================================================
# VERIFY SESSION OWNER
# =========================================================

def verify_session_owner(
    session_id: str,
    user_id: str
) -> bool:

    response = (
        supabase
        .table("chat_sessions")
        .select("session_id")
        .eq(
            "session_id",
            session_id
        )
        .eq(
            "user_id",
            user_id
        )
        .limit(1)
        .execute()
    )

    return bool(response.data)


# =========================================================
# SAVE MESSAGE
# =========================================================

def save_message(
    session_id: str,
    sender: str,
    content: str
):

    if not content:
        return None

    response = (
        supabase
        .table("chat_messages")
        .insert({
            "session_id": session_id,
            "sender": sender,
            "content": content
        })
        .execute()
    )

    return response.data


# =========================================================
# GET CHAT HISTORY
# =========================================================

def get_chat_history(
    session_id: str
):

    response = (
        supabase
        .table("chat_messages")
        .select(
            "message_id, sender, content, created_at"
        )
        .eq(
            "session_id",
            session_id
        )
        .order(
            "created_at",
            desc=False
        )
        .execute()
    )

    return response.data or []


# =========================================================
# RESTORE CHAT
# =========================================================

def restore_chat(
    session_id: str,
    user_id: str
):

    # Security check
    if not verify_session_owner(
        session_id,
        user_id
    ):
        raise PermissionError(
            "You cannot access this chat."
        )

    return get_chat_history(
        session_id
    )


# =========================================================
# DELETE CHAT
# =========================================================

def delete_chat(
    session_id: str,
    user_id: str
):

    # Security check
    if not verify_session_owner(
        session_id,
        user_id
    ):
        raise PermissionError(
            "You cannot delete this chat."
        )

    # Delete messages
    (
        supabase
        .table("chat_messages")
        .delete()
        .eq(
            "session_id",
            session_id
        )
        .execute()
    )

    # Delete chat session
    (
        supabase
        .table("chat_sessions")
        .delete()
        .eq(
            "session_id",
            session_id
        )
        .execute()
    )

    return True


# =========================================================
# VECTOR DATABASE
# =========================================================

def get_vectorstore():

    embeddings = get_embeddings()

    return Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )


# =========================================================
# WEB SEARCH
# =========================================================

def web_search(
    query: str
) -> str:

    try:

        results = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=8
        )

    except Exception as e:

        print("Tavily error:", e)

        return ""

    web_context = []

    for result in results.get(
        "results",
        []
    ):

        title = result.get(
            "title",
            ""
        )

        content = result.get(
            "content",
            ""
        )

        url = result.get(
            "url",
            ""
        )

        if not content:
            continue

        web_context.append(
            f"Title: {title}\n"
            f"Source: {url}\n"
            f"Information: {content}"
        )

    return "\n\n".join(
        web_context
    )


# =========================================================
# GET RAG CONTEXT
# =========================================================

def get_rag_context(
    query: str
) -> str:

    # Build vector database if it does not exist
    if not os.path.exists(
        "./chroma_db"
    ):
        build_vector_db()

    vector_store = get_vectorstore()

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 4
        }
    )

    docs = retriever.invoke(
        query
    )

    if not docs:
        return "No relevant study material was found."

    return "\n\n".join(
        doc.page_content
        for doc in docs
    )


# =========================================================
# ANSWER QUESTION
# =========================================================

def answer_question(
    query: str,
    session_id: str | None = None,
    user_id: str | None = None
) -> str:

    """
    Main AI Tutor pipeline.

    Supports:

    - Multiple users
    - Persistent chat sessions
    - Chat restoration
    - Quantum RAG
    - Web search
    - General AI
    """

    query = query.strip()

    if not query:
        return "Please enter a question."


    # =====================================================
    # SECURITY CHECK
    # =====================================================

    if session_id and user_id:

        if not verify_session_owner(
            session_id,
            user_id
        ):
            raise PermissionError(
                "This chat does not belong to this user."
            )


    # =====================================================
    # SAVE USER MESSAGE
    # =====================================================

    if session_id:

        save_message(
            session_id,
            "user",
            query
        )


    # =====================================================
    # CREATE LLM
    # =====================================================

    llm = get_llm()


    # =====================================================
    # ROUTER
    # =====================================================

    router_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a question router for an intelligent AI tutor.

Classify the user's question into exactly ONE category.

RAG
Questions specifically about:
- Quantum Computing
- Qiskit
- Quantum algorithms
- Quantum circuits
- Qubits
- Quantum study material

WEB
Questions about:
- Current events
- Latest information
- People
- Movies
- Companies
- Places
- Current facts
- Information requiring web verification

HYBRID
Questions requiring both:
- Quantum/Qiskit study material
AND
- Current external web information

GENERAL
Normal questions such as:
- Programming
- Mathematics
- Physics
- Writing
- General explanations

Return ONLY one word:

RAG
WEB
HYBRID
GENERAL
"""
        ),
        (
            "human",
            "{input}"
        )
    ])


    router_chain = (
        router_prompt
        | llm
        | StrOutputParser()
    )


    try:

        route = (
            router_chain
            .invoke(query)
            .strip()
            .upper()
        )

    except Exception:

        route = "GENERAL"


    if route not in {
        "RAG",
        "WEB",
        "HYBRID",
        "GENERAL"
    }:

        route = "GENERAL"


    # =====================================================
    # RAG CONTEXT
    # =====================================================

    rag_context = ""

    if route in {
        "RAG",
        "HYBRID"
    }:

        try:

            rag_context = get_rag_context(
                query
            )

        except Exception as e:

            print(
                "RAG error:",
                e
            )

            rag_context = (
                "No relevant study material "
                "could be retrieved."
            )


    # =====================================================
    # WEB CONTEXT
    # =====================================================

    web_context = ""

    if route in {
        "WEB",
        "HYBRID"
    }:

        web_context = web_search(
            query
        )

        if not web_context:

            web_context = (
                "No relevant web information "
                "was found."
            )


    # =====================================================
    # CHAT HISTORY
    # =====================================================

    history_str = ""

    if session_id:

        try:

            history = get_chat_history(
                session_id
            )

            # Last saved message is the current question.
            # Exclude it from previous conversation.
            recent_history = history[-7:-1]

            history_str = "\n".join(
                f"{message['sender']}: "
                f"{message['content']}"
                for message in recent_history
            )

        except Exception as e:

            print(
                "Chat history error:",
                e
            )


    # =====================================================
    # FINAL PROMPT
    # =====================================================

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are an intelligent and friendly AI Tutor.

Help students understand concepts clearly.

Rules:

- Give accurate answers.
- Do not invent information.
- Use study material when relevant.
- Use web information when relevant.
- For current information, prefer web information.
- Explain difficult concepts step-by-step.
- Keep explanations student-friendly.
- Use examples when helpful.
- If information is unavailable, say so clearly.
- Do not mention internal implementation details.

Never mention these internal systems to the student:

- RAG
- embeddings
- vector database
- Supabase
- routing system
- internal implementation

STUDY MATERIAL:
-------------------------
{rag_context}
-------------------------

WEB INFORMATION:
-------------------------
{web_context}
-------------------------

PREVIOUS CHAT:
-------------------------
{history}
-------------------------
"""
        ),
        (
            "human",
            "{input}"
        )
    ])


    chain = (
        {
            "rag_context": lambda _: rag_context,
            "web_context": lambda _: web_context,
            "history": lambda _: history_str,
            "input": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )


    # =====================================================
    # GENERATE ANSWER
    # =====================================================

    try:

        answer = chain.invoke(
            query
        )

    except Exception as e:

        print(
            "\nAI Error:",
            str(e)
        )

        answer = (
            "Sorry, I could not generate "
            "a response right now. "
            "Please try again."
        )


    # =====================================================
    # SAVE AI RESPONSE
    # =====================================================

    if session_id:

        save_message(
            session_id,
            "assistant",
            answer
        )


    return answer
