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

# Frontend-only attachment state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


# =========================================================
# FRONTEND CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap'
    );

    html, body, [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 8% 12%,
                rgba(99,102,241,0.20),
                transparent 26%
            ),
            radial-gradient(
                circle at 92% 10%,
                rgba(6,182,212,0.14),
                transparent 24%
            ),
            radial-gradient(
                circle at 78% 80%,
                rgba(139,92,246,0.15),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #020617 0%,
                #070b20 48%,
                #020617 100%
            );
    }


    /* =====================================================
       QUANTUM GRID
       ===================================================== */

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;

        background-image:
            linear-gradient(
                rgba(148,163,184,0.025) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(148,163,184,0.025) 1px,
                transparent 1px
            );

        background-size: 55px 55px;

        z-index: 0;
    }


    /* =====================================================
       GLOWING STARS
       ===================================================== */

    .stApp::after {
        content:
            "✦     ·       ✧          ·     ✦       ·        ✧"
            "       ·      ✦         ·          ✧      ·"
            "   ✧        ·       ✦       ·       ✧        ·"
            "       ·          ✦       ·       ✧       ·";

        position: fixed;

        top: 0;
        left: 0;

        width: 100%;
        height: 100%;

        pointer-events: none;

        color: rgba(196,181,253,0.35);

        font-size: 15px;

        line-height: 85px;

        letter-spacing: 45px;

        overflow: hidden;

        opacity: 0.45;

        text-shadow:
            0 0 8px rgba(167,139,250,0.8),
            0 0 18px rgba(99,102,241,0.4);

        z-index: 0;

        animation: starsMove 12s linear infinite;
    }

    @keyframes starsMove {

        0% {
            transform: translateY(0);
        }

        50% {
            transform: translateY(-18px);
        }

        100% {
            transform: translateY(0);
        }
    }


    /* =====================================================
       MAIN CONTAINER
       ===================================================== */

    .main .block-container {
        max-width: 1250px;

        padding-top: 1.5rem;

        padding-bottom: 7rem;

        position: relative;

        z-index: 1;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #030611 0%,
                #070b1d 55%,
                #02040c 100%
            );

        border-right:
            1px solid rgba(139,92,246,0.20);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }


    /* =====================================================
       SIDEBAR BUTTONS
       ===================================================== */

    section[data-testid="stSidebar"] .stButton button {

        min-height: 42px;

        border-radius: 12px;

        border:
            1px solid rgba(139,92,246,0.18);

        background:
            linear-gradient(
                135deg,
                rgba(18,25,53,0.96),
                rgba(7,12,29,0.96)
            );

        color: #dbeafe;

        font-weight: 500;

        transition:
            all 0.2s ease;
    }

    section[data-testid="stSidebar"] .stButton button:hover {

        border-color:
            rgba(139,92,246,0.60);

        background:
            linear-gradient(
                135deg,
                rgba(38,30,82,0.98),
                rgba(12,20,46,0.98)
            );

        transform:
            translateY(-1px);

        box-shadow:
            0 8px 25px rgba(0,0,0,0.3),
            0 0 20px rgba(139,92,246,0.12);
    }


    /* =====================================================
       SIDEBAR BRAND
       ===================================================== */

    .sidebar-logo {

        text-align: center;

        font-size: 50px;

        line-height: 1;

        margin-bottom: 5px;

        text-shadow:
            0 0 10px rgba(255,255,255,0.8),
            0 0 22px rgba(139,92,246,0.9),
            0 0 45px rgba(99,102,241,0.7);

        animation:
            logoPulse 3s ease-in-out infinite;
    }

    @keyframes logoPulse {

        0%, 100% {
            transform: scale(1);
        }

        50% {
            transform: scale(1.07);
        }
    }


    /* =====================================================
       MAIN QUANTUM LOGO
       ===================================================== */

    .quantum-logo {

        text-align: center;

        font-size: 78px;

        line-height: 1;

        margin-top: 8px;

        margin-bottom: 8px;

        text-shadow:
            0 0 10px rgba(255,255,255,0.9),
            0 0 22px rgba(139,92,246,0.95),
            0 0 45px rgba(99,102,241,0.8),
            0 0 80px rgba(59,130,246,0.45);

        animation:
            quantumPulse 3s ease-in-out infinite;
    }

    @keyframes quantumPulse {

        0%, 100% {
            transform: scale(1);
            filter: brightness(1);
        }

        50% {
            transform: scale(1.08);
            filter: brightness(1.25);
        }
    }


    /* =====================================================
       ONLINE BADGE
       ===================================================== */

    .online {

        width: fit-content;

        margin: 0 auto 20px auto;

        padding:
            6px 14px;

        border-radius: 999px;

        background:
            rgba(34,197,94,0.06);

        border:
            1px solid rgba(34,197,94,0.20);

        color:
            #86efac;

        font-size: 10px;

        font-weight: 700;

        letter-spacing: 1.8px;
    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {

        text-align: center;

        font-family:
            "Space Grotesk",
            sans-serif;

        font-size:
            clamp(34px,5vw,58px);

        font-weight: 700;

        letter-spacing: 5px;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #c4b5fd,
                #93c5fd,
                #ffffff
            );

        -webkit-background-clip: text;

        -webkit-text-fill-color: transparent;

        margin-top: 5px;
    }


    /* =====================================================
       SUBTITLE
       ===================================================== */

    .subtitle {

        text-align: center;

        max-width: 760px;

        margin:
            14px auto 24px auto;

        color:
            #94a3b8;

        font-size: 14px;

        line-height: 1.8;
    }


    /* =====================================================
       QUANTUM LINE
       ===================================================== */

    .quantum-line {

        width: 220px;

        height: 1px;

        margin:
            0 auto 24px auto;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(139,92,246,0.8),
                rgba(59,130,246,0.8),
                transparent
            );

        box-shadow:
            0 0 12px rgba(139,92,246,0.35);
    }


    /* =====================================================
       CHAT MESSAGES
       ===================================================== */

    [data-testid="stChatMessage"] {

        border-radius: 16px;

        border:
            1px solid rgba(139,92,246,0.10);

        background:
            linear-gradient(
                135deg,
                rgba(15,23,42,0.82),
                rgba(7,12,28,0.82)
            );

        margin-bottom: 10px;

        transition:
            all 0.2s ease;
    }

    [data-testid="stChatMessage"]:hover {

        border-color:
            rgba(139,92,246,0.28);

        box-shadow:
            0 5px 25px rgba(0,0,0,0.18);
    }

    [data-testid="stChatMessage"] p {

        color:
            #dbe4f0;

        line-height:
            1.7;
    }


    /* =====================================================
       PROMPT AREA
       ===================================================== */

    .prompt-shell {

        background:
            linear-gradient(
                135deg,
                rgba(12,18,40,0.97),
                rgba(5,10,25,0.97)
            );

        border:
            1px solid rgba(139,92,246,0.25);

        border-radius:
            18px;

        padding:
            7px;

        box-shadow:
            0 15px 50px rgba(0,0,0,0.35),
            0 0 25px rgba(99,102,241,0.08);
    }


    /* =====================================================
       CHAT INPUT
       ===================================================== */

    [data-testid="stChatInput"] > div {

        background:
            linear-gradient(
                135deg,
                rgba(12,18,38,0.98),
                rgba(5,10,25,0.98)
            );

        border:
            1px solid rgba(139,92,246,0.25);

        border-radius:
            16px;

        box-shadow:
            none;
    }

    [data-testid="stChatInput"] > div:focus-within {

        border-color:
            rgba(139,92,246,0.70);

        box-shadow:
            0 0 0 1px rgba(139,92,246,0.18),
            0 0 25px rgba(99,102,241,0.10);
    }

    [data-testid="stChatInput"] textarea {

        color:
            #f8fafc !important;

        font-size:
            14px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {

        color:
            #64748b !important;
    }


    /* =====================================================
       ATTACHMENT POPOVER
       ===================================================== */

    [data-testid="stPopover"] button {

        border-radius:
            12px;

        border:
            1px solid rgba(139,92,246,0.22);

        background:
            rgba(12,18,40,0.92);

        color:
            #e2e8f0;

        font-size:
            18px;

        transition:
            all 0.2s ease;
    }

    [data-testid="stPopover"] button:hover {

        border-color:
            rgba(139,92,246,0.65);

        background:
            rgba(30,27,75,0.95);

        box-shadow:
            0 0 18px rgba(139,92,246,0.18);
    }


    /* =====================================================
       POPOVER CONTENT
       ===================================================== */

    div[data-baseweb="popover"] {

        background:
            #080d20 !important;

        border:
            1px solid rgba(139,92,246,0.25) !important;

        border-radius:
            16px !important;

        box-shadow:
            0 20px 60px rgba(0,0,0,0.55) !important;
    }


    /* =====================================================
       ATTACHMENT OPTIONS
       ===================================================== */

    .attach-title {

        font-family:
            "Space Grotesk",
            sans-serif;

        font-size:
            17px;

        font-weight:
            600;

        color:
            #f8fafc;

        margin-bottom:
            5px;
    }

    .attach-description {

        color:
            #64748b;

        font-size:
            12px;

        margin-bottom:
            12px;
    }


    /* =====================================================
       ATTACHMENT CARD
       ===================================================== */

    .attachment-card {

        padding:
            10px 12px;

        border-radius:
            11px;

        border:
            1px solid rgba(139,92,246,0.12);

        background:
            rgba(15,23,42,0.55);

        margin:
            5px 0;

        color:
            #cbd5e1;

        font-size:
            12px;
    }


    /* =====================================================
       MICROPHONE
       ===================================================== */

    .mic-label {

        text-align:
            center;

        color:
            #94a3b8;

        font-size:
            11px;

        margin-top:
            5px;
    }


    /* =====================================================
       NORMAL BUTTONS
       ===================================================== */

    .stButton button {

        border-radius:
            11px;

        transition:
            all 0.2s ease;
    }

    .stButton button:hover {

        transform:
            translateY(-1px);
    }


    /* =====================================================
       ALERTS
       ===================================================== */

    div[data-testid="stAlert"] {

        border-radius:
            13px;
    }


    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {

        border-color:
            rgba(255,255,255,0.06);
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 768px) {

        .main-title {

            font-size:
                31px;

            letter-spacing:
                2px;
        }

        .subtitle {

            font-size:
                13px;
        }

        .quantum-logo {

            font-size:
                60px;
        }
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
        '<div class="quantum-logo">⚛️</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-title">QUANTUM AI TUTOR</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="subtitle">
            Explore quantum computing through an intelligent
            RAG-powered learning environment.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="online">🟢 AI TUTOR ONLINE</div>',
        unsafe_allow_html=True,
    )

    st.subheader("🔐 Login")

    email = st.text_input(
        "Enter your email",
        placeholder="student@example.com",
    )

    if st.button(
        "🚀 Start Learning",
        use_container_width=True,
    ):

        if not email.strip():

            st.error(
                "Please enter your email."
            )

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

            except Exception:

                st.error(
                    "Unable to complete login. "
                    "Please check your connection and try again."
                )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-logo">⚛️</div>',
        unsafe_allow_html=True,
    )

    st.title("QUANTUM LAB")

    st.caption(
        "AI LEARNING ENVIRONMENT"
    )

    st.markdown(
        f"🟢  {st.session_state.user_email}"
    )

    st.divider()


    # -----------------------------------------------------
    # WORKSPACE
    # -----------------------------------------------------

    st.caption("WORKSPACE")

    if st.button(
        "＋  New Quantum Session",
        use_container_width=True,
    ):

        try:

            session_id = create_chat_session(
                st.session_state.user_id
            )

            st.session_state.session_id = session_id

            st.session_state.messages = []

            st.session_state.uploaded_files = []

            st.rerun()

        except Exception:

            st.error(
                "Unable to create a new chat right now."
            )


    # -----------------------------------------------------
    # LOAD SESSIONS
    # -----------------------------------------------------

    try:

        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )

    except Exception:

        st.session_state.sessions = []

        st.warning(
            "Chat history is temporarily unavailable."
        )


    # -----------------------------------------------------
    # SESSION LIST
    # -----------------------------------------------------

    st.caption("YOUR SESSIONS")

    if not st.session_state.sessions:

        st.caption(
            "No saved sessions available."
        )

    else:

        for chat in st.session_state.sessions:

            session_id = chat["session_id"]

            title = chat.get(
                "title",
                "New Quantum Chat"
            )

            if st.button(
                f"◈  {title}",
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

                    st.session_state.uploaded_files = []

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

                except Exception:

                    st.error(
                        "Unable to open this chat right now."
                    )


    st.divider()


    # -----------------------------------------------------
    # CHAT SETTINGS
    # -----------------------------------------------------

    if st.session_state.session_id:

        st.caption("CHAT SETTINGS")

        new_title = st.text_input(
            "Rename chat",
            placeholder="Enter new chat name",
        )

        if st.button(
            "✎  Rename Chat",
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
                        "Chat renamed successfully."
                    )

                    st.rerun()

                except Exception:

                    st.error(
                        "Unable to rename this chat."
                    )


        if st.button(
            "🗑️  Delete Chat",
            use_container_width=True,
        ):

            try:

                delete_chat(
                    st.session_state.session_id,
                    st.session_state.user_id,
                )

                st.session_state.session_id = None

                st.session_state.messages = []

                st.session_state.uploaded_files = []

                st.success(
                    "Chat deleted successfully."
                )

                st.rerun()

            except Exception:

                st.error(
                    "Unable to delete this chat."
                )


    st.divider()


    # -----------------------------------------------------
    # LOGOUT
    # -----------------------------------------------------

    if st.button(
        "↪  Logout",
        use_container_width=True,
    ):

        st.session_state.logged_in = False

        st.session_state.user_email = ""

        st.session_state.user_id = None

        st.session_state.session_id = None

        st.session_state.messages = []

        st.session_state.uploaded_files = []

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="quantum-logo">⚛️</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="online">🟢 AI TUTOR ONLINE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">QUANTUM AI TUTOR</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="quantum-line"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Learn quantum computing and technical concepts
        through an intelligent RAG-powered learning environment.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# REQUIRE CHAT
# =========================================================

if not st.session_state.session_id:

    st.info(
        "✨ Create a new quantum session from the sidebar to start learning."
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
# ATTACHMENT AREA
# =========================================================

# ---------------------------------------------------------
# SHOW CURRENT ATTACHMENTS
# ---------------------------------------------------------

if st.session_state.uploaded_files:

    st.markdown(
        "📎 **Attached:**"
    )

    for uploaded in st.session_state.uploaded_files:

        st.caption(
            f"• {uploaded.name}"
        )


# =========================================================
# PROMPT CONTROLS
# =========================================================

prompt_col1, prompt_col2 = st.columns(
    [1, 8]
)


# =========================================================
# PLUS ATTACHMENT BUTTON
# =========================================================

with prompt_col1:

    with st.popover(
        "＋",
        use_container_width=True,
    ):

        st.markdown(
            '<div class="attach-title">Add to your question</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="attach-description">Choose something to attach</div>',
            unsafe_allow_html=True,
        )


        # -------------------------------------------------
        # PHOTOS
        # -------------------------------------------------

        st.markdown(
            """
            <div class="attachment-card">
                🖼️ <b>Add photos</b><br>
                <span style="color:#64748b;">
                Upload images from your computer
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        photos = st.file_uploader(
            "Photos",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            accept_multiple_files=True,
            key="photo_uploader",
            label_visibility="collapsed",
        )


        # -------------------------------------------------
        # FILES
        # -------------------------------------------------

        st.markdown(
            """
            <div class="attachment-card">
                📄 <b>Add files</b><br>
                <span style="color:#64748b;">
                Upload PDF, TXT, DOCX or other files
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        documents = st.file_uploader(
            "Files",
            type=[
                "pdf",
                "txt",
                "docx",
                "csv",
                "py",
                "java",
                "c",
                "cpp",
                "md",
            ],
            accept_multiple_files=True,
            key="document_uploader",
            label_visibility="collapsed",
        )


        # -------------------------------------------------
        # SAVE ATTACHMENTS TO FRONTEND STATE
        # -------------------------------------------------

        selected_files = []

        if photos:

            selected_files.extend(
                photos
            )

        if documents:

            selected_files.extend(
                documents
            )

        if selected_files:

            st.session_state.uploaded_files = (
                selected_files
            )

            st.success(
                f"{len(selected_files)} attachment(s) added."
            )


# =========================================================
# MICROPHONE
# =========================================================

with prompt_col2:

    mic_col, input_col = st.columns(
        [1, 15]
    )

    with mic_col:

        st.markdown(
            """
            <div style="
                text-align:center;
                padding-top:8px;
                font-size:20px;
            ">
                🎙️
            </div>
            """,
            unsafe_allow_html=True,
        )

    with input_col:

        query = st.chat_input(
            "Ask your quantum question..."
        )


# =========================================================
# OPTIONAL VOICE INPUT
# =========================================================

with st.expander(
    "🎙️ Voice input",
    expanded=False,
):

    st.caption(
        "Record a voice message here. "
        "Your existing RAG pipeline is not modified."
    )

    audio_value = st.audio_input(
        "Record your question",
        label_visibility="collapsed",
    )

    if audio_value:

        st.success(
            "Voice recording captured."
        )

        st.caption(
            "Audio is currently kept in the frontend only. "
            "It is not sent to the RAG engine."
        )


# =========================================================
# PROCESS QUESTION
# =========================================================

if query:

    query = query.strip()

    if not query:

        st.stop()


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            query
        )

        # Show attachments visually,
        # but DO NOT send them to RAG.

        if st.session_state.uploaded_files:

            st.caption(
                "📎 "
                + ", ".join(
                    file.name
                    for file in st.session_state.uploaded_files
                )
            )


    # -----------------------------------------------------
    # RAG ANSWER
    # -----------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "🔎 Searching the quantum knowledge base..."
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

        st.markdown(
            answer
        )


    # -----------------------------------------------------
    # SAVE ANSWER
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    # Clear attachments after sending
    st.session_state.uploaded_files = []
