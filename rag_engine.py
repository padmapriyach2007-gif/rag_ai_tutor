import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tavily import TavilyClient


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


# =========================================================
# API KEYS / DATABASE SETTINGS
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
# VALIDATE REQUIRED SETTINGS
# =========================================================

if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN is missing.\n\n"
        "Add this to your .env file:\n"
        "HF_TOKEN=your_huggingface_token"
    )

if not TAVILY_API_KEY:
    raise ValueError(
        "TAVILY_API_KEY is missing.\n\n"
        "Add this to your .env file:\n"
        "TAVILY_API_KEY=your_tavily_key"
    )

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing.\n\n"
        "Add this to your .env file:\n"
        "SUPABASE_URL=your_supabase_url"
    )

if not SUPABASE_SERVICE_KEY:
    raise ValueError(
        "SUPABASE_SERVICE_KEY is missing.\n\n"
        "Add this to your .env file:\n"
        "SUPABASE_SERVICE_KEY=your_supabase_service_key"
    )


# =========================================================
# CONNECTIONS
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)

tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


# =========================================================
# AI MODEL
# =========================================================

def get_llm():
    """
    Hugging Face Router + GPT-OSS model.
    """

    return ChatOpenAI(
        model="openai/gpt-oss-120b",
        temperature=0.4,
        api_key=HF_TOKEN,
        base_url="https://router.huggingface.co/v1"
    )


# =========================================================
# USER MANAGEMENT
# =========================================================

def get_or_create_user(
    email: str,
    role: str = "student"
) -> str:

    email = email.strip().lower()

    if not email:
        raise ValueError("Email cannot be empty.")

    # -----------------------------------------------------
    # Check existing user
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Create new user
    # -----------------------------------------------------

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
# CHAT SESSION MANAGEMENT
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
# VERIFY CHAT OWNER
# =========================================================

def verify_session_owner(
    session_id: str,
    user_id: str
) -> bool:

    response = (
        supabase
        .table("chat_sessions")
        .select("session_id")
        .eq("session_id", session_id)
        .eq("user_id", user_id)
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
# WEB SEARCH
# =========================================================

def web_search(
    query: str
) -> str:

    try:

        results = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=6
        )

    except Exception as e:

        print(
            "Tavily error:",
            str(e)
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
# DETECT WHETHER WEB SEARCH IS NEEDED
# =========================================================

def needs_web_search(
    query: str
) -> bool:

    query_lower = query.lower()

    current_keywords = [
        "latest",
        "current",
        "today",
        "now",
        "recent",
        "recently",
        "news",
        "2026",
        "this year",
        "this month",
        "price",
        "weather",
        "stock",
        "market",
        "release",
        "released",
        "new version",
        "updated",
        "update",
        "who is the current",
        "what is happening",
    ]

    return any(
        keyword in query_lower
        for keyword in current_keywords
    )


# =========================================================
# GENERAL AI ANSWER
# =========================================================

def generate_answer(
    query: str,
    history: str = "",
    web_context: str = ""
) -> str:

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are Quantum AI Tutor, a highly capable and friendly
AI assistant for students.

Your job is to answer ANY question the user asks.

You can answer questions about:

- Quantum Computing
- Qiskit
- Qubits
- Quantum Algorithms
- Artificial Intelligence
- Machine Learning
- Python
- C
- C++
- Java
- JavaScript
- HTML
- CSS
- SQL
- Data Structures
- Algorithms
- Mathematics
- Physics
- Engineering
- Computer Science
- Programming
- Projects
- Assignments
- General knowledge
- Writing and explanations
- Other normal educational questions

IMPORTANT:

1. Do NOT say that you need study material.
2. Do NOT say "No relevant study material was found."
3. Do NOT depend on a local document or knowledge base.
4. Answer using your own knowledge.
5. If web information is provided, use it to improve
   accuracy for current topics.
6. Clearly explain concepts for students.
7. Use step-by-step explanations when useful.
8. For programming questions, provide correct code when
   requested and explain the important parts.
9. For mathematics, show the calculation steps.
10. If the question is ambiguous, make a reasonable
    interpretation and answer it.
11. Never mention internal implementation details such as
    LangChain, Supabase, Tavily, Hugging Face, prompts,
    vector databases, or RAG.
12. Do not pretend that information is current if it is
    not supported by the provided web information.

PREVIOUS CONVERSATION:
----------------------
{history}
----------------------

CURRENT WEB INFORMATION:
----------------------
{web_context}
----------------------
"""
        ),
        (
            "human",
            "{input}"
        )
    ])

    chain = (
        prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke({
        "history": history,
        "web_context": web_context,
        "input": query
    })


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
        return "Please enter a question."

    # =====================================================
    # VERIFY SESSION
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
    # LOAD CHAT HISTORY
    # =====================================================

    history_str = ""

    if session_id:

        try:

            history = get_chat_history(
                session_id
            )

            # Don't duplicate the current question
            recent_history = history[-8:-1]

            history_str = "\n".join(
                f"{message['sender']}: "
                f"{message['content']}"
                for message in recent_history
            )

        except Exception as e:

            print(
                "Chat history error:",
                str(e)
            )

    # =====================================================
    # OPTIONAL WEB SEARCH
    # =====================================================

    web_context = ""

    if needs_web_search(query):

        web_context = web_search(
            query
        )

        if not web_context:

            web_context = (
                "No web information was available. "
                "Answer using your general knowledge."
            )

    # =====================================================
    # GENERATE ANSWER
    # =====================================================

    try:

        answer = generate_answer(
            query=query,
            history=history_str,
            web_context=web_context
        )

    except Exception as e:

        print(
            "\nAI Error:",
            str(e)
        )

        answer = (
            "Sorry, I could not generate a response "
            "right now.\n\n"
            f"Error: {str(e)}"
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
