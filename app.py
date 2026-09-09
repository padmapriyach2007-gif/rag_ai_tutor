import streamlit as st
from pathlib import Path

from rag_engine import (
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    verify_session_owner,
    rename_chat,
    delete_chat,
    get_chat_history,
    answer_question,
    ingest_text_file
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Quantum AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main background */

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(80, 80, 150, 0.15),
                transparent 35%
            ),
            radial-gradient(
                circle at bottom right,
                rgba(50, 100, 180, 0.10),
                transparent 35%
            );
    }


    /* Hero */

    .hero {
        text-align: center;
        padding: 40px 20px 25px 20px;
    }


    .hero-icon {
        font-size: 55px;
        margin-bottom: 5px;
    }


    .hero-title {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: 2px;
    }


    .hero-subtitle {
        font-size: 17px;
        opacity: 0.7;
        margin-top: 5px;
    }


    .online {
        margin-top: 15px;
        font-size: 14px;
        font-weight: 600;
    }


    /* Learning header */

    .learning-header {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.04);
        margin-bottom: 20px;
    }


    .learning-icon {
        font-size: 30px;
        display: inline-block;
        margin-right: 10px;
    }


    .learning-title {
        font-size: 24px;
        font-weight: 700;
    }


    .learning-description {
        opacity: 0.7;
        margin-top: 5px;
    }


    /* Chat messages */

    .user-message {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        background: rgba(80, 100, 180, 0.20);
        border: 1px solid rgba(100, 120, 220, 0.25);
    }


    .assistant-message {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
    }


    /* Sidebar */

    .sidebar-title {
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 15px;
    }


    /* Source */

    .source-box {
        padding: 10px;
        border-radius: 10px;
        background: rgba(255,255,255,0.04);
        margin-top: 10px;
        font-size: 13px;
        opacity: 0.8;
    }

    </style>
    """,
    unsafe_allow_html=True
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

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Quantum Chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "learning_mode" not in st.session_state:
    st.session_state.learning_mode = True


# =========================================================
# LOGIN
# =========================================================

if not st.session_state.logged_in:

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
        "🚀 Start Learning",
        use_container_width=True
    ):

        if not email.strip():

            st.error(
                "Please enter your email."
            )

        else:

            try:

                user_id = get_or_create_user(
                    email=email,
                    role="student"
                )

                st.session_state.user_id = user_id
                st.session_state.user_email = email
                st.session_state.logged_in = True

                st.rerun()

            except Exception as e:

                st.error(
                    f"Unable to login: {e}"
                )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            ⚛️ Quantum Lab
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        st.session_state.user_email
    )

    st.divider()

    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        try:

            session_id = create_chat_session(
                st.session_state.user_id,
                "New Quantum Chat"
            )

            st.session_state.current_session_id = session_id
            st.session_state.chat_title = "New Quantum Chat"
            st.session_state.messages = []

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not create chat: {e}"
            )


    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    st.markdown("### 💬 Your Chats")

    sessions = []

    try:

        sessions = get_user_sessions(
            st.session_state.user_id
        )

    except Exception as e:

        st.error(
            f"Could not load chats: {e}"
        )


    for session in sessions:

        session_id = session.get(
            "session_id"
        )

        title = session.get(
            "title",
            "New Chat"
        )

        if st.button(
            f"💬 {title}",
            key=f"chat_{session_id}",
            use_container_width=True
        ):

            try:

                history = get_chat_history(
                    session_id
                )

                st.session_state.current_session_id = session_id
                st.session_state.chat_title = title

                st.session_state.messages = []

                for message in history:

                    role = message.get(
                        "sender"
                    )

                    content = message.get(
                        "content"
                    )

                    if role in [
                        "user",
                        "assistant"
                    ]:

                        st.session_state.messages.append(
                            {
                                "role": role,
                                "content": content
                            }
                        )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not restore chat: {e}"
                )


    st.divider()


    # -----------------------------------------------------
    # CHAT ACTIONS
    # -----------------------------------------------------

    if st.session_state.current_session_id:

        st.markdown("### ⚙️ Chat Actions")

        new_title = st.text_input(
            "Rename chat",
            value=st.session_state.chat_title,
            key="rename_input"
        )

        if st.button(
            "✏️ Rename Chat",
            use_container_width=True
        ):

            try:

                rename_chat(
                    st.session_state.current_session_id,
                    st.session_state.user_id,
                    new_title
                )

                st.session_state.chat_title = new_title

                st.success(
                    "Chat renamed."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    str(e)
                )


        if st.button(
            "🗑️ Delete Chat",
            use_container_width=True
        ):

            try:

                delete_chat(
                    st.session_state.current_session_id,
                    st.session_state.user_id
                )

                st.session_state.current_session_id = None
                st.session_state.chat_title = "New Quantum Chat"
                st.session_state.messages = []

                st.rerun()

            except Exception as e:

                st.error(
                    str(e)
                )


    st.divider()


    # -----------------------------------------------------
    # LEARNING MODE
    # -----------------------------------------------------

    st.markdown("### 🧠 Learning Mode")

    st.session_state.learning_mode = st.toggle(
        "Enable Learning Mode",
        value=st.session_state.learning_mode
    )


    if st.session_state.learning_mode:

        st.caption(
            "Answers are explained in a simple, "
            "student-friendly way."
        )


    st.divider()


    # -----------------------------------------------------
    # LOGOUT
    # -----------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_id = None
        st.session_state.current_session_id = None
        st.session_state.messages = []

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

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


# =========================================================
# LEARNING HEADER
# =========================================================

st.markdown(
    """
    <div class="learning-header">

        <span class="learning-icon">
            🧠
        </span>

        <span class="learning-title">
            Learning Mode
        </span>

        <div class="learning-description">
            Ask questions and learn concepts step by step.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# NO CHAT SELECTED
# =========================================================

if not st.session_state.current_session_id:

    st.info(
        "Create a new chat from the sidebar to start learning."
    )


# =========================================================
# DISPLAY CHAT
# =========================================================

for message in st.session_state.messages:

    role = message.get(
        "role"
    )

    content = message.get(
        "content",
        ""
    )

    if role == "user":

        with st.chat_message(
            "user"
        ):

            st.markdown(content)

    else:

        with st.chat_message(
            "assistant"
        ):

            st.markdown(content)


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Ask your AI Tutor anything..."
)


# =========================================================
# PROCESS QUESTION
# =========================================================

if prompt:

    # -----------------------------------------------------
    # CREATE SESSION AUTOMATICALLY
    # -----------------------------------------------------

    if not st.session_state.current_session_id:

        try:

            session_id = create_chat_session(
                st.session_state.user_id,
                "New Quantum Chat"
            )

            st.session_state.current_session_id = session_id
            st.session_state.chat_title = "New Quantum Chat"

        except Exception as e:

            st.error(
                f"Could not create chat: {e}"
            )

            st.stop()


    # -----------------------------------------------------
    # DISPLAY USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(prompt)


    # -----------------------------------------------------
    # GENERATE RAG ANSWER
    # -----------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "🔎 Searching knowledge base..."
        ):

            try:

                answer = answer_question(
                    query=prompt,
                    session_id=st.session_state.current_session_id,
                    user_id=st.session_state.user_id
                )

            except Exception as e:

                answer = (
                    "⚠️ Something went wrong.\n\n"
                    f"`{str(e)}`"
                )

        st.markdown(answer)


    # -----------------------------------------------------
    # SAVE TO UI STATE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
