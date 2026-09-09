import streamlit as st

from rag_engine import (
    answer_question,
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    restore_chat,
    rename_chat,
    delete_chat,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Quantum Lab | AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
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

if "sessions" not in st.session_state:
    st.session_state.sessions = []


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-top: 10px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        opacity: 0.8;
        margin-bottom: 20px;
    }

    .online {
        text-align: center;
        color: #00ff88;
        font-weight: bold;
        margin-bottom: 30px;
    }

    .stChatMessage {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="main-title">
            ⚛️ QUANTUM AI TUTOR
        </div>

        <div class="subtitle">
            Explore quantum computing through conversation
        </div>

        <div class="online">
            ● AI TUTOR ONLINE
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Login")

    email = st.text_input(
        "Enter your email",
        placeholder="student@example.com",
    )

    if st.button(
        "Start Learning 🚀",
        use_container_width=True,
    ):

        if not email.strip():

            st.error("Please enter your email.")

        else:

            try:

                user_id = get_or_create_user(
                    email.strip()
                )

                st.session_state.logged_in = True
                st.session_state.user_email = (
                    email.strip().lower()
                )
                st.session_state.user_id = user_id
                st.session_state.session_id = None
                st.session_state.messages = []

                st.rerun()

            except Exception as e:

                st.error(
                    f"Login failed: {str(e)}"
                )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚛️ Quantum Lab")

    st.write(
        f"👤 {st.session_state.user_email}"
    )

    st.divider()

    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True,
    ):

        try:

            session_id = create_chat_session(
                st.session_state.user_id
            )

            st.session_state.session_id = session_id
            st.session_state.messages = []

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not create chat: {str(e)}"
            )

    # -----------------------------------------------------
    # LOAD CHAT SESSIONS
    # -----------------------------------------------------

    try:

        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )

    except Exception as e:

        st.error(
            f"Could not load chats: {str(e)}"
        )

    st.subheader("💬 Your Chats")

    for chat in st.session_state.sessions:

        session_id = chat["session_id"]
        title = chat.get(
            "title",
            "New Quantum Chat"
        )

        if st.button(
            title,
            key=f"chat_{session_id}",
            use_container_width=True,
        ):

            try:

                history = restore_chat(
                    session_id,
                    st.session_state.user_id
                )

                st.session_state.session_id = (
                    session_id
                )

                st.session_state.messages = []

                for message in history:

                    st.session_state.messages.append(
                        {
                            "role": (
                                "user"
                                if message["sender"] == "user"
                                else "assistant"
                            ),
                            "content": message["content"],
                        }
                    )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not open chat: {str(e)}"
                )

    st.divider()

    # -----------------------------------------------------
    # CHAT MANAGEMENT
    # -----------------------------------------------------

    if st.session_state.session_id:

        st.subheader("⚙️ Chat Settings")

        new_title = st.text_input(
            "Rename chat",
            placeholder="Enter new chat name",
        )

        if st.button(
            "Rename",
            use_container_width=True,
        ):

            if not new_title.strip():

                st.warning(
                    "Enter a chat name."
                )

            else:

                try:

                    rename_chat(
                        st.session_state.session_id,
                        st.session_state.user_id,
                        new_title,
                    )

                    st.success(
                        "Chat renamed."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Rename failed: {str(e)}"
                    )

        if st.button(
            "🗑️ Delete Chat",
            use_container_width=True,
        ):

            try:

                delete_chat(
                    st.session_state.session_id,
                    st.session_state.user_id,
                )

                st.session_state.session_id = None
                st.session_state.messages = []

                st.success(
                    "Chat deleted."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Delete failed: {str(e)}"
                )

    st.divider()

    # -----------------------------------------------------
    # LOGOUT
    # -----------------------------------------------------

    if st.button(
        "Logout",
        use_container_width=True,
    ):

        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_id = None
        st.session_state.session_id = None
        st.session_state.messages = []

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """
    <div class="main-title">
        ⚛️ QUANTUM AI TUTOR
    </div>

    <div class="subtitle">
        Learn quantum computing and other technical subjects
        with an AI-powered RAG tutor
    </div>

    <div class="online">
        ● AI TUTOR ONLINE
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# REQUIRE CHAT
# =========================================================

if not st.session_state.session_id:

    st.info(
        "Create a new chat from the sidebar to start learning."
    )

    st.stop()


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

query = st.chat_input(
    "Ask your question..."
)


if query:

    query = query.strip()

    if not query:
        st.stop()

    # -----------------------------------------------------
    # DISPLAY USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):

        st.markdown(query)

    # -----------------------------------------------------
    # GENERATE RAG ANSWER
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🔎 Searching knowledge base..."
        ):

            try:

                answer = answer_question(
                    query=query,
                    session_id=st.session_state.session_id,
                    user_id=st.session_state.user_id,
                )

            except Exception as e:

                answer = (
                    "⚠️ Sorry, something went wrong.\n\n"
                    f"`{str(e)}`"
                )

        st.markdown(answer)

    # -----------------------------------------------------
    # SAVE TO UI STATE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
