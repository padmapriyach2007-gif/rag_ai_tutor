import streamlit as st

from rag_engine import (
    get_or_create_user,
    create_chat_session,
    get_user_sessions,
    restore_chat,
    delete_chat,
    rename_chat,
    answer_question
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Lab | AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(110, 80, 255, 0.18),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(0, 200, 255, 0.12),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #070714 0%,
            #0b0b1f 50%,
            #080817 100%
        );

    color: #f5f5ff;
}


[data-testid="stHeader"] {
    background: transparent;
}


[data-testid="stMain"] {
    background: transparent;
}


/* =====================================================
   SIDEBAR
   ===================================================== */

[data-testid="stSidebar"] {

    background:
        rgba(8, 8, 24, 0.97);

    border-right:
        1px solid
        rgba(150, 120, 255, 0.18);
}


.sidebar-brand {

    text-align: center;

    padding:
        10px 5px 25px 5px;
}


.sidebar-logo {

    font-size: 48px;

    margin-bottom: 5px;
}


.sidebar-title {

    font-size: 22px;

    font-weight: 800;

    letter-spacing: 1px;

    color: white;
}


.sidebar-subtitle {

    color: #9999bb;

    font-size: 13px;

    margin-top: 5px;
}


/* =====================================================
   SIDEBAR CARDS
   ===================================================== */

.side-card {

    background:
        linear-gradient(
            145deg,
            rgba(100, 80, 220, 0.15),
            rgba(20, 20, 55, 0.45)
        );

    border:
        1px solid
        rgba(130, 110, 255, 0.22);

    border-radius: 15px;

    padding: 15px;

    margin: 12px 0;
}


.side-card-title {

    font-weight: 700;

    margin-bottom: 7px;

    color: white;
}


.side-card-text {

    color: #aaaac4;

    font-size: 13px;

    line-height: 1.5;
}


/* =====================================================
   SIDEBAR BUTTONS
   ===================================================== */

[data-testid="stSidebar"] .stButton > button {

    width: 100%;

    border-radius: 10px;

    min-height: 42px;

    background:
        rgba(45, 40, 85, 0.55);

    border:
        1px solid
        rgba(140, 120, 255, 0.25);

    color: white;

    transition:
        all 0.2s ease;
}


[data-testid="stSidebar"] .stButton > button:hover {

    background:
        rgba(65, 58, 115, 0.65);

    border-color:
        rgba(160, 140, 255, 0.65);

    transform:
        translateY(-1px);
}


/* =====================================================
   HERO
   ===================================================== */

.hero-box {

    background:
        linear-gradient(
            145deg,
            rgba(40, 35, 85, 0.65),
            rgba(15, 15, 38, 0.78)
        );

    border:
        1px solid
        rgba(140, 120, 255, 0.20);

    border-radius: 22px;

    padding: 55px 20px;

    text-align: center;

    margin-top: 25px;

    margin-bottom: 25px;

    box-shadow:
        0 20px 60px
        rgba(0, 0, 0, 0.25);
}


.hero-icon {

    font-size: 58px;

    line-height: 1;

    margin-bottom: 12px;

    filter:
        drop-shadow(
            0 0 18px
            rgba(120, 100, 255, 0.7)
        );
}


.hero-title {

    font-size:
        clamp(32px, 5vw, 54px);

    font-weight: 850;

    letter-spacing: -1px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #b9b1ff,
            #8be9ff
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;
}


.hero-subtitle {

    font-size: 16px;

    color: #a9a9c4;

    margin-top: 10px;
}


.online {

    display: inline-block;

    margin-top: 18px;

    padding:
        7px 15px;

    border-radius: 30px;

    background:
        rgba(80, 220, 160, 0.08);

    border:
        1px solid
        rgba(80, 220, 160, 0.25);

    color: #8ff0bd;

    font-size: 12px;

    font-weight: 600;
}


/* =====================================================
   WELCOME
   ===================================================== */

.welcome-card {

    max-width: 850px;

    margin:
        20px auto 25px auto;

    padding: 28px;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            rgba(40, 35, 85, 0.65),
            rgba(15, 15, 38, 0.78)
        );

    border:
        1px solid
        rgba(140, 120, 255, 0.20);

    box-shadow:
        0 20px 60px
        rgba(0, 0, 0, 0.25);
}


.welcome-title {

    font-size: 23px;

    font-weight: 750;

    margin-bottom: 8px;
}


.welcome-text {

    color: #b4b4cc;

    line-height: 1.6;

    font-size: 14px;
}


/* =====================================================
   CHAT
   ===================================================== */

[data-testid="stChatMessage"] {

    border-radius: 18px;

    padding:
        5px 10px;

    margin-bottom: 8px;
}


[data-testid="stChatMessageContent"] {

    font-size: 15px;

    line-height: 1.65;
}


/* =====================================================
   CHAT INPUT
   ===================================================== */

[data-testid="stChatInput"] {

    border-radius: 18px;
}


[data-testid="stChatInput"] textarea {

    background:
        rgba(20, 20, 45, 0.85);

    border:
        1px solid
        rgba(140, 120, 255, 0.25);

    border-radius: 16px;

    color: white;
}


/* =====================================================
   FOOTER
   ===================================================== */

.footer {

    text-align: center;

    color: #666681;

    font-size: 11px;

    margin-top: 35px;

    padding-bottom: 15px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="login-box">

            <div class="hero-icon">
                ⚛️
            </div>

            <h1 style="color:white;">
                Quantum Lab
            </h1>

            <p style="color:#a9a9c4;">
                AI-Powered Learning Space
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🔐 Login")

    email = st.text_input(
        "Email address",
        placeholder="Enter your email",
        key="login_email"
    )

    if st.button(
        "🚀 Login",
        use_container_width=True
    ):

        email = email.strip().lower()

        if not email:

            st.error(
                "Please enter your email address."
            )

        else:

            try:

                user_id = get_or_create_user(
                    email
                )

                sessions = get_user_sessions(
                    user_id
                )

                if not sessions:

                    session_id = create_chat_session(
                        user_id,
                        "Quantum Learning"
                    )

                else:

                    session_id = sessions[0][
                        "session_id"
                    ]

                st.session_state.user_email = email

                st.session_state.user_id = user_id

                st.session_state.session_id = session_id

                st.session_state.logged_in = True

                st.toast(
                    "Login successful!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Login failed: {str(e)}"
                )

    st.markdown(
        """
        <div class="footer">
            Quantum Lab • AI Tutor
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # BRAND
    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo">
                ⚛️
            </div>

            <div class="sidebar-title">
                QUANTUM LAB
            </div>

            <div class="sidebar-subtitle">
                AI-Powered Learning Space
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # USER
    st.markdown("---")

    st.write("👤 **Logged In**")

    st.caption(
        st.session_state.user_email
    )

    # NEW CHAT
    st.markdown("---")

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        try:

            new_session_id = (
                create_chat_session(
                    st.session_state.user_id,
                    "New Quantum Chat"
                )
            )

            st.session_state.session_id = (
                new_session_id
            )

            st.toast(
                "New chat created!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not create chat: {str(e)}"
            )

    # LOAD CHATS
    try:

        sessions = get_user_sessions(
            st.session_state.user_id
        )

    except Exception as e:

        sessions = []

        st.error(
            f"Could not load chats: {str(e)}"
        )

    # YOUR CHATS
    st.markdown("---")

    st.subheader("💬 Your Chats")

    if not sessions:

        st.caption(
            "No chats available."
        )

    for session in sessions:

        session_id = session[
            "session_id"
        ]

        title = session.get(
            "title",
            "Untitled Chat"
        )

        is_current = (
            session_id
            ==
            st.session_state.session_id
        )

        if is_current:

            button_text = (
                f"🟣 {title}"
            )

        else:

            button_text = (
                f"💬 {title}"
            )

        if st.button(
            button_text,
            key=f"open_{session_id}",
            use_container_width=True
        ):

            st.session_state.session_id = (
                session_id
            )

            st.rerun()

    # RENAME CHAT
    st.markdown("---")

    with st.expander(
        "✏️ Rename Current Chat"
    ):

        current_session = None

        for session in sessions:

            if (
                session["session_id"]
                ==
                st.session_state.session_id
            ):

                current_session = session

                break

        if current_session:

            current_title = current_session.get(
                "title",
                "Untitled Chat"
            )

            new_name = st.text_input(
                "New chat name",
                value=current_title,
                key="rename_input"
            )

            if st.button(
                "Save New Name",
                use_container_width=True
            ):

                new_name = new_name.strip()

                if not new_name:

                    st.error(
                        "Chat name cannot be empty."
                    )

                elif new_name == current_title:

                    st.info(
                        "This is already the current name."
                    )

                else:

                    try:

                        rename_chat(
                            st.session_state.session_id,
                            st.session_state.user_id,
                            new_name
                        )

                        st.toast(
                            "Chat renamed!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Rename failed: {str(e)}"
                        )

        else:

            st.info(
                "Select a chat first."
            )

    # DELETE CURRENT CHAT
    st.markdown("---")

    if st.button(
        "🗑️ Delete Current Chat",
        use_container_width=True
    ):

        try:

            current_session_id = (
                st.session_state.session_id
            )

            delete_chat(
                current_session_id,
                st.session_state.user_id
            )

            remaining_sessions = (
                get_user_sessions(
                    st.session_state.user_id
                )
            )

            if remaining_sessions:

                st.session_state.session_id = (
                    remaining_sessions[0][
                        "session_id"
                    ]
                )

            else:

                new_session_id = (
                    create_chat_session(
                        st.session_state.user_id,
                        "Quantum Learning"
                    )
                )

                st.session_state.session_id = (
                    new_session_id
                )

            st.toast(
                "Chat deleted!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Delete failed: {str(e)}"
            )

    # CLEAR CURRENT CONVERSATION
    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True
    ):

        try:

            current_session_id = (
                st.session_state.session_id
            )

            delete_chat(
                current_session_id,
                st.session_state.user_id
            )

            new_session_id = (
                create_chat_session(
                    st.session_state.user_id,
                    "New Quantum Chat"
                )
            )

            st.session_state.session_id = (
                new_session_id
            )

            st.toast(
                "Conversation cleared!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not clear conversation: {str(e)}"
            )

    # LOGOUT
    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_id = None
        st.session_state.session_id = None

        st.rerun()

    # LEARNING MODE
    st.markdown("---")

    st.markdown(
        """
        <div class="side-card">

            <div class="side-card-title">
                🧠 Learning Mode
            </div>

            <div class="side-card-text">

                Ask questions about:

                <br><br>

                • Quantum Computing
                <br>
                • Qubits
                <br>
                • Quantum Gates
                <br>
                • Quantum Circuits
                <br>
                • Qiskit
                <br>
                • Programming
                <br>
                • Mathematics
                <br>
                • Science
                <br>
                • General Knowledge

            </div>

        </div>


        <div class="side-card">

            <div class="side-card-title">
                📚 Knowledge + Web
            </div>

            <div class="side-card-text">

                The AI uses conversation history
                and Tavily web search when current
                information is required.

            </div>

        </div>


        <div class="side-card">

            <div class="side-card-title">
                ✨ AI Tutor
            </div>

            <div class="side-card-text">

                Ask questions naturally.
                The AI is not restricted to
                predefined questions.

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero-box">

        <div class="hero-icon">
            ⚛️
        </div>

        <div class="hero-title">
            Quantum AI Tutor
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


# ============================================================
# CURRENT CHAT
# ============================================================

current_session_id = (
    st.session_state.session_id
)


# ============================================================
# RESTORE CHAT HISTORY
# ============================================================

try:

    messages = restore_chat(
        current_session_id,
        st.session_state.user_id
    )

except Exception as e:

    st.error(
        f"Could not load conversation: {str(e)}"
    )

    messages = []


# ============================================================
# WELCOME SCREEN
# ============================================================

if not messages:

    st.markdown(
        """
        <div class="welcome-card">

            <div class="welcome-title">
                👋 Welcome to your Quantum Learning Space
            </div>

            <div class="welcome-text">

                I'm your AI tutor.

                Ask me to explain a concept,
                solve a problem, explain code,
                simplify a difficult topic,
                or explore quantum computing
                step by step.

                <br><br>

                You can also ask questions outside
                quantum computing.

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### 💡 Try asking"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "⚛️ What is a qubit?",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "What is a qubit?"
            )

            st.rerun()

        if st.button(
            "🌌 Explain quantum superposition",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "Explain quantum superposition"
            )

            st.rerun()

    with col2:

        if st.button(
            "🔗 What is quantum entanglement?",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "What is quantum entanglement?"
            )

            st.rerun()

        if st.button(
            "🐣 Explain quantum computing like I'm a beginner",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "Explain quantum computing like I'm a beginner"
            )

            st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in messages:

    sender = message.get(
        "sender",
        ""
    )

    content = message.get(
        "content",
        ""
    )

    if not content:
        continue

    if sender == "user":

        with st.chat_message(
            "user",
            avatar="👩‍💻"
        ):

            st.markdown(
                content
            )

    else:

        with st.chat_message(
            "assistant",
            avatar="⚛️"
        ):

            st.markdown(
                content
            )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask anything..."
)


# ============================================================
# EXAMPLE QUESTION
# ============================================================

if st.session_state.pending_question:

    question = (
        st.session_state.pending_question
    )

    st.session_state.pending_question = None


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    question = question.strip()

    if question:

        # Display user message
        with st.chat_message(
            "user",
            avatar="👩‍💻"
        ):

            st.markdown(
                question
            )

        # Generate AI response
        with st.chat_message(
            "assistant",
            avatar="⚛️"
        ):

            with st.spinner(
                "🧠 Analyzing your question..."
            ):

                try:

                    answer = answer_question(
                        query=question,
                        session_id=(
                            st.session_state.session_id
                        ),
                        user_id=(
                            st.session_state.user_id
                        )
                    )

                except Exception as e:

                    answer = (
                        "⚠️ I couldn't process "
                        "your question right now.\n\n"
                        f"**Error:** `{str(e)}`"
                    )

            st.markdown(
                answer
            )

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        ⚛️ Powered by Groq + Tavily + Supabase
        • Quantum Lab AI Tutor

    </div>
    """,
    unsafe_allow_html=True
)
