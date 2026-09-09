import streamlit as st
from pathlib import Path

from rag_engine import (
    answer_question,
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    restore_chat,
    rename_chat,
    delete_chat,
    add_files_to_rag
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Quantum Lab | AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "files_indexed" not in st.session_state:
    st.session_state.files_indexed = False


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main page */

    .main {
        background-color: #ffffff;
    }

    /* Hero */

    .hero {
        text-align: center;
        padding: 25px 10px 10px 10px;
    }

    .hero-icon {
        font-size: 60px;
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: 2px;
    }

    .hero-subtitle {
        font-size: 18px;
        margin-top: 5px;
        opacity: 0.7;
    }

    .online {
        margin-top: 12px;
        font-size: 14px;
        font-weight: 600;
    }

    /* Learning mode */

    .learning-header {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid rgba(128,128,128,0.2);
    }

    .learning-icon {
        font-size: 22px;
        display: inline-block;
        margin-right: 8px;
    }

    .learning-title {
        font-size: 20px;
        font-weight: 700;
    }

    .learning-text {
        opacity: 0.7;
        font-size: 14px;
    }

    /* File information */

    .rag-info {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.2);
        margin-top: 10px;
        margin-bottom: 10px;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.2);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    st.markdown(
        """
        <div class="hero">

            <div class="hero-icon">
                ⚛️
            </div>

            <div class="hero-title">
                QUANTUM AI TUTOR
            </div>

            <div class="hero-subtitle">
                Explore quantum computing through conversation
            </div>

            <div class="online">
                ● AI TUTOR ONLINE
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("Welcome")

    email = st.text_input(
        "Enter your email",
        placeholder="student@example.com"
    )

    if st.button(
        "Login",
        use_container_width=True,
        type="primary"
    ):

        if not email.strip():

            st.error(
                "Please enter your email."
            )

            return

        try:

            user_id = get_or_create_user(
                email=email
            )

            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.user_id = user_id

            # Create first chat session

            sessions = get_user_sessions(
                user_id
            )

            if sessions:

                st.session_state.session_id = (
                    sessions[0]["session_id"]
                )

                history = restore_chat(
                    st.session_state.session_id,
                    user_id
                )

                st.session_state.messages = []

                for message in history:

                    st.session_state.messages.append(
                        {
                            "role": message["sender"],
                            "content": message["content"]
                        }
                    )

            else:

                session_id = create_chat_session(
                    user_id
                )

                st.session_state.session_id = session_id
                st.session_state.messages = []

            st.rerun()

        except Exception as e:

            st.error(
                f"Login failed: {str(e)}"
            )


# =========================================================
# NEW CHAT
# =========================================================

def new_chat():

    if not st.session_state.user_id:
        return

    try:

        session_id = create_chat_session(
            st.session_state.user_id
        )

        st.session_state.session_id = session_id
        st.session_state.messages = []

        st.rerun()

    except Exception as e:

        st.error(
            f"Could not create new chat: {str(e)}"
        )


# =========================================================
# LOAD CHAT
# =========================================================

def load_chat(session_id):

    try:

        history = restore_chat(
            session_id,
            st.session_state.user_id
        )

        st.session_state.session_id = session_id

        st.session_state.messages = []

        for message in history:

            st.session_state.messages.append(
                {
                    "role": message["sender"],
                    "content": message["content"]
                }
            )

        st.rerun()

    except Exception as e:

        st.error(
            f"Could not restore chat: {str(e)}"
        )


# =========================================================
# RENAME CURRENT CHAT
# =========================================================

def rename_current_chat():

    sessions = get_user_sessions(
        st.session_state.user_id
    )

    current_session = None

    for session in sessions:

        if session["session_id"] == st.session_state.session_id:

            current_session = session
            break

    if not current_session:
        return

    new_title = st.text_input(
        "New chat name",
        value=current_session["title"],
        key="rename_input"
    )

    if st.button(
        "Save name",
        use_container_width=True
    ):

        try:

            rename_chat(
                st.session_state.session_id,
                st.session_state.user_id,
                new_title
            )

            st.success(
                "Chat renamed successfully."
            )

            st.rerun()

        except Exception as e:

            st.error(
                str(e)
            )


# =========================================================
# CHAT SIDEBAR
# =========================================================

def sidebar():

    with st.sidebar:

        st.markdown(
            "## ⚛️ Quantum Lab"
        )

        st.caption(
            "RAG-powered AI Tutor"
        )

        st.divider()

        # -------------------------------------------------
        # USER
        # -------------------------------------------------

        st.write(
            f"👤 {st.session_state.user_email}"
        )

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_id = None
            st.session_state.session_id = None
            st.session_state.messages = []

            st.rerun()

        st.divider()

        # -------------------------------------------------
        # NEW CHAT
        # -------------------------------------------------

        if st.button(
            "➕ New Chat",
            use_container_width=True
        ):

            new_chat()

        st.divider()

        # -------------------------------------------------
        # CHAT HISTORY
        # -------------------------------------------------

        st.subheader(
            "💬 Your Chats"
        )

        sessions = get_user_sessions(
            st.session_state.user_id
        )

        if not sessions:

            st.caption(
                "No previous chats."
            )

        else:

            for session in sessions:

                title = session.get(
                    "title",
                    "New Quantum Chat"
                )

                if st.button(
                    title,
                    key=f"chat_{session['session_id']}",
                    use_container_width=True
                ):

                    load_chat(
                        session["session_id"]
                    )

        st.divider()

        # -------------------------------------------------
        # CHAT MANAGEMENT
        # -------------------------------------------------

        st.subheader(
            "⚙️ Chat Management"
        )

        with st.expander(
            "Rename Chat"
        ):

            rename_current_chat()

        if st.button(
            "🗑️ Delete Current Chat",
            use_container_width=True
        ):

            if st.session_state.session_id:

                try:

                    delete_chat(
                        st.session_state.session_id,
                        st.session_state.user_id
                    )

                    sessions = get_user_sessions(
                        st.session_state.user_id
                    )

                    if sessions:

                        st.session_state.session_id = (
                            sessions[0]["session_id"]
                        )

                        history = restore_chat(
                            st.session_state.session_id,
                            st.session_state.user_id
                        )

                        st.session_state.messages = []

                        for message in history:

                            st.session_state.messages.append(
                                {
                                    "role": message["sender"],
                                    "content": message["content"]
                                }
                            )

                    else:

                        new_id = create_chat_session(
                            st.session_state.user_id
                        )

                        st.session_state.session_id = new_id
                        st.session_state.messages = []

                    st.rerun()

                except Exception as e:

                    st.error(
                        str(e)
                    )

        # -------------------------------------------------
        # CLEAR CHAT
        # -------------------------------------------------

        if st.button(
            "🧹 Clear Chat",
            use_container_width=True
        ):

            st.session_state.messages = []

            st.rerun()

        st.divider()

        # -------------------------------------------------
        # RAG FILE UPLOAD
        # -------------------------------------------------

        st.subheader(
            "📚 Study Materials"
        )

        st.caption(
            "Upload files for the AI Tutor to learn from."
        )

        uploaded_files = st.file_uploader(
            "Upload documents",
            type=[
                "pdf",
                "txt",
                "docx",
                "csv",
                "xlsx",
                "py",
                "java",
                "c",
                "cpp",
                "sql",
                "md",
                "html",
                "css",
                "js",
                "json"
            ],
            accept_multiple_files=True,
            key="rag_uploader"
        )

        # -------------------------------------------------
        # INDEX FILES
        # -------------------------------------------------

        if uploaded_files:

            if st.button(
                "📥 Add Files to Knowledge Base",
                use_container_width=True,
                type="primary"
            ):

                with st.spinner(
                    "Reading and indexing your files..."
                ):

                    results = add_files_to_rag(
                        uploaded_files
                    )

                st.session_state.uploaded_files = [
                    file.name
                    for file in uploaded_files
                ]

                st.session_state.files_indexed = True

                for result in results:

                    if result["status"] == "Indexed successfully":

                        st.success(
                            f"✅ {result['filename']} "
                            f"({result['chunks']} chunks)"
                        )

                    else:

                        st.error(
                            f"❌ {result['filename']}: "
                            f"{result['status']}"
                        )

        # -------------------------------------------------
        # DISPLAY INDEXED FILES
        # -------------------------------------------------

        if st.session_state.uploaded_files:

            st.markdown(
                """
                <div class="rag-info">
                    <b>📖 Knowledge Base</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            for filename in st.session_state.uploaded_files:

                st.caption(
                    f"📄 {filename}"
                )


# =========================================================
# MAIN CHAT UI
# =========================================================

def chat_page():

    sidebar()

    st.markdown(
        """
        <div class="hero">

            <div class="hero-icon">
                ⚛️
            </div>

            <div class="hero-title">
                QUANTUM AI TUTOR
            </div>

            <div class="hero-subtitle">
                Explore quantum computing through conversation
            </div>

            <div class="online">
                ● AI TUTOR ONLINE
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="learning-header">

            <span class="learning-icon">
                🧠
            </span>

            <span class="learning-title">
                RAG Learning Mode
            </span>

            <br>

            <span class="learning-text">
                Ask questions about your uploaded
                study materials or any topic.
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # DISPLAY CHAT
    # -----------------------------------------------------

    for message in st.session_state.messages:

        role = message["role"]

        if role == "user":

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    message["content"]
                )

        else:

            with st.chat_message(
                "assistant"
            ):

                st.markdown(
                    message["content"]
                )

    # -----------------------------------------------------
    # USER INPUT
    # -----------------------------------------------------

    user_query = st.chat_input(
        "Ask your AI Tutor anything..."
    )

    if user_query:

        # Display user message

        with st.chat_message(
            "user"
        ):

            st.markdown(
                user_query
            )

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_query
            }
        )

        # Generate response

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Thinking..."
            ):

                try:

                    answer = answer_question(
                        query=user_query,
                        session_id=st.session_state.session_id,
                        user_id=st.session_state.user_id
                    )

                except Exception as e:

                    answer = (
                        "⚠️ Something went wrong.\n\n"
                        f"`{str(e)}`"
                    )

                st.markdown(
                    answer
                )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# =========================================================
# APPLICATION
# =========================================================

if not st.session_state.logged_in:

    login_page()

else:

    chat_page()
