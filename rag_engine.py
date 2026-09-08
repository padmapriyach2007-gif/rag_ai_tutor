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

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)


# =========================================================
# GET API KEYS
# =========================================================

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
        SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY")

except Exception:
    pass


# =========================================================
# VALIDATE REQUIRED KEYS
# =========================================================

missing_keys = []

if not HF_TOKEN:
    missing_keys.append("HF_TOKEN")

if not TAVILY_API_KEY:
    missing_keys.append("TAVILY_API_KEY")

if not SUPABASE_URL:
    missing_keys.append("SUPABASE_URL")

if not SUPABASE_SERVICE_KEY:
    missing_keys.append("SUPABASE_SERVICE_KEY")

if missing_keys:
    raise ValueError(
        "Missing environment variables: "
        + ", ".join(missing_keys)
        + "\n\n"
        "Add them to your .env file."
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
    """
    Hugging Face Router LLM.

    Uses the Hugging Face token instead of Gemini.
    """

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
    """
    Local Hugging Face embedding model.

    No Gemini API key is required.
    """

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
# GET USER CHAT SESSIONS
# =========================================================

def get_user_sessions(user_id: str):

    response = (
        supabase
        .table("chat_sessions")
        .select(
            "session_id, title, created_at"
        )
        .eq("user_id", user_id)
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

    if not verify_session_owner(
        session_id,
        user_id
    ):
        raise PermissionError(
            "You cannot delete this chat."
        )

    # Delete messages first
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

    # Delete session
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
# VECTOR STORE
# =========================================================

def get_vectorstore():

    embeddings = get_embeddings()

    return Chroma(
        persist_directory=str(
            BASE_DIR / "chroma_db"
        ),
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

        print(
            "Tavily error:",
            e
        )

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
            f"""
Title: {title}

Source: {url}

Information:
{content}
"""
        )

    return "\n\n".join(
        web_context
    )


# =========================================================
# RAG SEARCH
# =========================================================

def get_rag_context(
    query: str
) -> str:

    chroma_path = (
        BASE_DIR / "chroma_db"
    )

    # Build database if it doesn't exist
    if not chroma_path.exists():

        print(
            "Chroma DB not found."
        )

        build_vector_db()

    try:

        vector_store = (
            get_vectorstore()
        )

        retriever = (
            vector_store
            .as_retriever(
                search_kwargs={
                    "k": 4
                }
            )
        )

        docs = retriever.invoke(
            query
        )

    except Exception as e:

        print(
            "RAG retrieval error:",
            e
        )

        return (
            "No relevant study material "
            "could be retrieved."
        )

    if not docs:

        return (
            "No relevant study material "
            "was found."
        )

    return "\n\n".join(
        doc.page_content
        for doc in docs
    )


# =========================================================
# QUESTION ROUTER
# =========================================================

def classify_question(
    query: str,
    llm
) -> str:

    router_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a question router for an intelligent AI tutor.

Classify the user's question into exactly ONE category:

RAG
Questions about quantum computing, Qiskit,
quantum algorithms, qubits, quantum circuits,
or information that should come from study material.

WEB
Current events, latest information,
current companies, current technologies,
places, recent facts, or information requiring
the internet.

HYBRID
Questions requiring both study material
and web information.

GENERAL
Normal programming, Python, Java, C,
physics, mathematics, writing,
or general explanations.

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
        ]
    )

    chain = (
        router_prompt
        | llm
        | StrOutputParser()
    )

    try:

        route = (
            chain
            .invoke({
                "input": query
            })
            .strip()
            .upper()
        )

    except Exception as e:

        print(
            "Router error:",
            e
        )

        route = "GENERAL"

    if route not in {
        "RAG",
        "WEB",
        "HYBRID",
        "GENERAL"
    }:
        route = "GENERAL"

    return route


# =========================================================
# MAIN ANSWER FUNCTION
# =========================================================

def answer_question(
    query: str,
    session_id: str | None = None,
    user_id: str | None = None
) -> str:

    query = query.strip()

    if not query:

        return (
            "Please enter a question."
        )

    # -----------------------------------------------------
    # Verify session ownership
    # -----------------------------------------------------

    if session_id and user_id:

        if not verify_session_owner(
            session_id,
            user_id
        ):

            raise PermissionError(
                "This chat does not belong to this user."
            )

    # -----------------------------------------------------
    # Save user message
    # -----------------------------------------------------

    if session_id:

        save_message(
            session_id,
            "user",
            query
        )

    # -----------------------------------------------------
    # Create LLM
    # -----------------------------------------------------

    llm = get_llm()

    # -----------------------------------------------------
    # Classify question
    # -----------------------------------------------------

    route = classify_question(
        query,
        llm
    )

    print(
        f"Question route: {route}"
    )

    # -----------------------------------------------------
    # RAG context
    # -----------------------------------------------------

    rag_context = ""

    if route in {
        "RAG",
        "HYBRID"
    }:

        rag_context = get_rag_context(
            query
        )

    # -----------------------------------------------------
    # WEB context
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    history_str = ""

    if session_id:

        try:

            history = get_chat_history(
                session_id
            )

            # Avoid duplicating the current question
            recent_history = history[-8:-1]

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

    # -----------------------------------------------------
    # FINAL PROMPT
    # -----------------------------------------------------

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an intelligent, friendly,
and accurate AI Tutor.

Your job is to help students understand
concepts clearly and step-by-step.

Use the provided study material when it
is relevant.

Use web information when it is provided.

If study material is unavailable, you can
still answer general questions using your
knowledge.

IMPORTANT:
- Do not mention RAG.
- Do not mention Chroma.
- Do not mention embeddings.
- Do not mention Supabase.
- Do not mention vector databases.
- Do not mention internal routing.
- Explain concepts naturally.
- For beginner questions, use simple language.
- Give examples when useful.
- Use equations/code when appropriate.

STUDY MATERIAL
=========================
{rag_context}
=========================

WEB INFORMATION
=========================
{web_context}
=========================

PREVIOUS CHAT
=========================
{history}
=========================
"""
            ),
            (
                "human",
                "{input}"
            )
        ]
    )

    # -----------------------------------------------------
    # FINAL CHAIN
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # GENERATE ANSWER
    # -----------------------------------------------------

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
            "a response right now.\n\n"
            f"Error: {str(e)}"
        )

    # -----------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # -----------------------------------------------------

    if session_id:

        save_message(
            session_id,
            "assistant",
            answer
        )

    return answer
