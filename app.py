import streamlit as st
import io

# =========================================================
# OPTIONAL MICROPHONE / SPEECH RECOGNITION
# =========================================================

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


# =========================================================
# YOUR EXISTING RAG + DATABASE IMPORTS
# DO NOT CHANGE
# =========================================================

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

# ---------------------------------------------------------
# FRONTEND ONLY
# ---------------------------------------------------------

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None


# =========================================================
# FRONTEND CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GOOGLE FONTS
       ===================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap'
    );


    /* =====================================================
       GLOBAL
       ===================================================== */

    html,
    body,
    [class*="css"] {

        font-family:
            "Inter",
            sans-serif;
    }


    .stApp {

        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(99,102,241,0.20),
                transparent 27%
            ),

            radial-gradient(
                circle at 90% 12%,
                rgba(6,182,212,0.14),
                transparent 25%
            ),

            radial-gradient(
                circle at 78% 82%,
                rgba(139,92,246,0.18),
                transparent 30%
            ),

            linear-gradient(
                135deg,
                #020617 0%,
                #080b24 48%,
                #020617 100%
            );

        min-height:
            100vh;
    }


    /* =====================================================
       QUANTUM GRID
       ===================================================== */

    .stApp::before {

        content:
            "";

        position:
            fixed;

        inset:
            0;

        pointer-events:
            none;

        background-image:

            linear-gradient(
                rgba(129,140,248,0.025) 1px,
                transparent 1px
            ),

            linear-gradient(
                90deg,
                rgba(129,140,248,0.025) 1px,
                transparent 1px
            );

        background-size:
            55px 55px;

        z-index:
            0;
    }


    /* =====================================================
       STAR FIELD
       ===================================================== */

    .quantum-stars {

        position:
            fixed;

        inset:
            0;

        pointer-events:
            none;

        overflow:
            hidden;

        z-index:
            0;
    }


    .star {

        position:
            absolute;

        color:
            #ddd6fe;

        font-size:
            9px;

        opacity:
            0.45;

        text-shadow:
            0 0 6px rgba(196,181,253,0.9),
            0 0 15px rgba(99,102,241,0.8);

        animation:
            twinkle 3s ease-in-out infinite;
    }


    .star:nth-child(1)  { left: 4%;  top: 12%; animation-delay: .2s; }
    .star:nth-child(2)  { left: 11%; top: 30%; animation-delay: 1.4s; }
    .star:nth-child(3)  { left: 18%; top: 68%; animation-delay: .8s; }
    .star:nth-child(4)  { left: 27%; top: 18%; animation-delay: 2s; }
    .star:nth-child(5)  { left: 35%; top: 42%; animation-delay: .5s; }
    .star:nth-child(6)  { left: 43%; top: 10%; animation-delay: 1.7s; }
    .star:nth-child(7)  { left: 51%; top: 72%; animation-delay: .9s; }
    .star:nth-child(8)  { left: 59%; top: 28%; animation-delay: 2.3s; }
    .star:nth-child(9)  { left: 66%; top: 55%; animation-delay: .4s; }
    .star:nth-child(10) { left: 73%; top: 15%; animation-delay: 1.2s; }
    .star:nth-child(11) { left: 81%; top: 39%; animation-delay: 2.1s; }
    .star:nth-child(12) { left: 88%; top: 74%; animation-delay: .7s; }
    .star:nth-child(13) { left: 94%; top: 22%; animation-delay: 1.8s; }
    .star:nth-child(14) { left: 47%; top: 52%; animation-delay: 1s; }
    .star:nth-child(15) { left: 7%;  top: 82%; animation-delay: 2.5s; }

    @keyframes twinkle {

        0%, 100% {

            opacity:
                0.18;

            transform:
                scale(0.8);
        }

        50% {

            opacity:
                0.85;

            transform:
                scale(1.5);
        }
    }


    /* =====================================================
       MAIN CONTAINER
       ===================================================== */

    .main .block-container {

        max-width:
            1250px;

        padding-top:
            1.2rem;

        padding-bottom:
            7rem;

        position:
            relative;

        z-index:
            1;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #030611,
                #070b1d,
                #02040c
            );

        border-right:
            1px solid rgba(139,92,246,0.20);
    }


    section[data-testid="stSidebar"] .stButton button {

        min-height:
            42px;

        border-radius:
            12px;

        border:
            1px solid rgba(139,92,246,0.18);

        background:
            linear-gradient(
                135deg,
                rgba(18,25,53,0.96),
                rgba(7,12,29,0.96)
            );

        color:
            #dbeafe;

        transition:
            all .2s ease;
    }


    section[data-testid="stSidebar"] .stButton button:hover {

        border-color:
            rgba(139,92,246,0.65);

        box-shadow:
            0 0 22px rgba(139,92,246,0.15);

        transform:
            translateY(-1px);
    }


    /* =====================================================
       SIDEBAR LOGO
       ===================================================== */

    .sidebar-logo {

        text-align:
            center;

        font-size:
            52px;

        margin-bottom:
            3px;

        text-shadow:
            0 0 10px rgba(255,255,255,.9),
            0 0 25px rgba(139,92,246,.95),
            0 0 50px rgba(99,102,241,.8);

        animation:
            quantumPulse 3s ease-in-out infinite;
    }


    /* =====================================================
       MAIN QUANTUM LOGO
       ===================================================== */

    .quantum-logo {

        text-align:
            center;

        font-size:
            75px;

        line-height:
            1;

        margin-top:
            8px;

        margin-bottom:
            8px;

        text-shadow:
            0 0 10px white,
            0 0 24px rgba(139,92,246,1),
            0 0 50px rgba(99,102,241,.85);

        animation:
            quantumPulse 3s ease-in-out infinite;
    }


    @keyframes quantumPulse {

        0%, 100% {

            transform:
                scale(1);

            filter:
                brightness(1);
        }

        50% {

            transform:
                scale(1.08);

            filter:
                brightness(1.25);
        }
    }


    /* =====================================================
       ONLINE BADGE
       ===================================================== */

    .online {

        width:
            fit-content;

        margin:
            0 auto 18px auto;

        padding:
            6px 14px;

        border-radius:
            999px;

        background:
            rgba(34,197,94,.06);

        border:
            1px solid rgba(34,197,94,.22);

        color:
            #86efac;

        font-size:
            10px;

        font-weight:
            700;

        letter-spacing:
            1.8px;

        box-shadow:
            0 0 18px rgba(34,197,94,.06);
    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {

        text-align:
            center;

        font-family:
            "Space Grotesk",
            sans-serif;

        font-size:
            clamp(34px, 5vw, 58px);

        font-weight:
            700;

        letter-spacing:
            5px;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #c4b5fd,
                #93c5fd,
                #ffffff
            );

        -webkit-background-clip:
            text;

        -webkit-text-fill-color:
            transparent;
    }


    /* =====================================================
       SUBTITLE
       ===================================================== */

    .subtitle {

        text-align:
            center;

        max-width:
            780px;

        margin:
            12px auto 20px auto;

        color:
            #94a3b8;

        font-size:
            14px;

        line-height:
            1.8;
    }


    .quantum-line {

        width:
            230px;

        height:
            1px;

        margin:
            0 auto 20px auto;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(139,92,246,.85),
                rgba(59,130,246,.85),
                transparent
            );

        box-shadow:
            0 0 14px rgba(139,92,246,.4);
    }


    /* =====================================================
       CHAT MESSAGES
       ===================================================== */

    [data-testid="stChatMessage"] {

        border-radius:
            16px;

        border:
            1px solid rgba(139,92,246,.10);

        background:
            linear-gradient(
                135deg,
                rgba(15,23,42,.82),
                rgba(7,12,28,.82)
            );

        margin-bottom:
            10px;

        transition:
            all .2s ease;
    }


    [data-testid="stChatMessage"]:hover {

        border-color:
            rgba(139,92,246,.28);

        box-shadow:
            0 5px 25px rgba(0,0,0,.18);
    }


    [data-testid="stChatMessage"] p {

        color:
            #dbe4f0;

        line-height:
            1.7;
    }


    /* =====================================================
       PROMPT ROW
       ===================================================== */

    .prompt-wrapper {

        position:
            relative;

        margin-top:
            18px;

        padding:
            5px;

        border-radius:
            20px;

        background:
            linear-gradient(
                135deg,
                rgba(17,24,50,.98),
                rgba(4,9,25,.98)
            );

        border:
            1px solid rgba(139,92,246,.30);

        box-shadow:
            0 15px 55px rgba(0,0,0,.40),
            0 0 30px rgba(99,102,241,.08);
    }


    /* =====================================================
       CHAT INPUT
       ===================================================== */

    [data-testid="stChatInput"] {

        margin:
            0 !important;
    }


    [data-testid="stChatInput"] > div {

        background:
            transparent !important;

        border:
            none !important;

        box-shadow:
            none !important;
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
       PLUS BUTTON
       ===================================================== */

    .plus-button button {

        height:
            46px !important;

        min-height:
            46px !important;

        width:
            46px !important;

        border-radius:
            50% !important;

        border:
            1px solid rgba(139,92,246,.35) !important;

        background:
            radial-gradient(
                circle,
                rgba(139,92,246,.22),
                rgba(15,23,42,.95)
            ) !important;

        color:
            #ddd6fe !important;

        font-size:
            22px !important;

        box-shadow:
            0 0 15px rgba(139,92,246,.10);

        transition:
            all .25s ease !important;
    }


    .plus-button button:hover {

        transform:
            rotate(90deg)
            scale(1.08);

        border-color:
            rgba(167,139,250,.85) !important;

        box-shadow:
            0 0 25px rgba(139,92,246,.35) !important;
    }


    /* =====================================================
       MICROPHONE
       ===================================================== */

    .mic-container {

        display:
            flex;

        justify-content:
            center;

        align-items:
            center;

        height:
            46px;
    }


    .mic-container button {

        border-radius:
            50% !important;

        border:
            1px solid rgba(59,130,246,.35) !important;

        background:
            radial-gradient(
                circle,
                rgba(59,130,246,.20),
                rgba(15,23,42,.96)
            ) !important;

        color:
            #bfdbfe !important;

        box-shadow:
            0 0 15px rgba(59,130,246,.10);

        transition:
            all .25s ease;
    }


    .mic-container button:hover {

        border-color:
            rgba(96,165,250,.9) !important;

        box-shadow:
            0 0 28px rgba(59,130,246,.35);

        transform:
            scale(1.08);
    }


    /* =====================================================
       POPOVER
       ===================================================== */

    div[data-baseweb="popover"] {

        background:
            #080d20 !important;

        border:
            1px solid rgba(139,92,246,.28) !important;

        border-radius:
            18px !important;

        box-shadow:
            0 25px 70px rgba(0,0,0,.60) !important;
    }


    /* =====================================================
       ATTACHMENT MENU
       ===================================================== */

    .attach-heading {

        font-family:
            "Space Grotesk",
            sans-serif;

        color:
            #f8fafc;

        font-size:
            17px;

        font-weight:
            600;

        margin-bottom:
            3px;
    }


    .attach-subheading {

        color:
            #64748b;

        font-size:
            12px;

        margin-bottom:
            12px;
    }


    .attach-option {

        padding:
            11px;

        margin:
            5px 0;

        border-radius:
            12px;

        background:
            rgba(15,23,42,.65);

        border:
            1px solid rgba(139,92,246,.12);

        transition:
            all .2s ease;
    }


    .attach-option:hover {

        background:
            rgba(30,27,75,.8);

        border-color:
            rgba(139,92,246,.35);
    }


    .attach-icon {

        font-size:
            20px;

        margin-right:
            8px;
    }


    .attach-name {

        color:
            #e2e8f0;

        font-weight:
            600;

        font-size:
            13px;
    }


    .attach-desc {

        color:
            #64748b;

        font-size:
            11px;
    }


    /* =====================================================
       FILE UPLOADER
       ===================================================== */

    [data-testid="stFileUploader"] {

        margin-top:
            4px;
    }


    /* =====================================================
       SIDEBAR INPUTS
       ===================================================== */

    section[data-testid="stSidebar"] input {

        background:
            rgba(10,16,35,.9) !important;

        color:
            #e2e8f0 !important;

        border-radius:
            10px !important;
    }


    /* =====================================================
       ALERTS
       ===================================================== */

    div[data-testid="stAlert"] {

        border-radius:
            13px;
    }


    /* =====================================================
       RESPONSIVE
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
                58px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# BACKGROUND STARS
# =========================================================

st.markdown(
    """
    <div class="quantum-stars">

        <span class="star">✦</span>
        <span class="star">·</span>
        <span class="star">✧</span>
        <span class="star">·</span>
        <span class="star">✦</span>
        <span class="star">·</span>
        <span class="star">✧</span>
        <span class="star">✦</span>
        <span class="star">·</span>
        <span class="star">✧</span>
        <span class="star">·</span>
        <span class="star">✦</span>
        <span class="star">✧</span>
        <span class="star">·</span>
        <span class="star">✦</span>

    </div>
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

                # =================================================
                # EXISTING DATABASE FUNCTION — UNCHANGED
                # =================================================

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

    st.markdown(
        '<div class="sidebar-logo">⚛️</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            font-family:'Space Grotesk';
            font-weight:700;
            font-size:19px;
            color:#e9d5ff;
            letter-spacing:2px;
        ">
            QUANTUM LAB
        </div>

        <div style="
            text-align:center;
            color:#64748b;
            font-size:9px;
            letter-spacing:2px;
            margin-bottom:18px;
        ">
            AI LEARNING ENVIRONMENT
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="
            padding:10px 12px;
            border-radius:12px;
            border:1px solid rgba(139,92,246,.16);
            background:rgba(15,23,42,.65);
            color:#cbd5e1;
            font-size:12px;
        ">
            <span style="color:#22c55e;">●</span>
            &nbsp;{st.session_state.user_email}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()


    # =====================================================
    # NEW CHAT
    # =====================================================

    st.caption("WORKSPACE")

    if st.button(
        "＋  New Quantum Session",
        use_container_width=True,
    ):

        try:

            # =================================================
            # EXISTING DATABASE FUNCTION — UNCHANGED
            # =================================================

            session_id = create_chat_session(
                st.session_state.user_id
            )

            st.session_state.session_id = session_id

            st.session_state.messages = []

            st.session_state.uploaded_files = []

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not create chat: {str(e)}"
            )


    # =====================================================
    # LOAD EXISTING CHATS
    # =====================================================

    try:

        # =================================================
        # EXISTING DATABASE FUNCTION — UNCHANGED
        # =================================================

        st.session_state.sessions = get_user_sessions(
            st.session_state.user_id
        )

    except Exception:

        st.session_state.sessions = []

        st.warning(
            "Chat history is temporarily unavailable."
        )


    st.caption("YOUR SESSIONS")


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

                # =================================================
                # EXISTING DATABASE FUNCTION — UNCHANGED
                # =================================================

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
                            "role":
                                (
                                    "user"
                                    if message["sender"] == "user"
                                    else "assistant"
                                ),

                            "content":
                                message["content"],
                        }
                    )

                st.session_state.uploaded_files = []

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not open chat: {str(e)}"
                )


    st.divider()


    # =====================================================
    # CHAT SETTINGS
    # =====================================================

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

                    # =============================================
                    # EXISTING DATABASE FUNCTION — UNCHANGED
                    # =============================================

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
            "🗑️  Delete Chat",
            use_container_width=True,
        ):

            try:

                # =============================================
                # EXISTING DATABASE FUNCTION — UNCHANGED
                # =============================================

                delete_chat(
                    st.session_state.session_id,
                    st.session_state.user_id,
                )

                st.session_state.session_id = None

                st.session_state.messages = []

                st.session_state.uploaded_files = []

                st.success(
                    "Chat deleted."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Delete failed: {str(e)}"
                )


    st.divider()


    # =====================================================
    # LOGOUT
    # =====================================================

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
# REQUIRE ACTIVE CHAT
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
# ATTACHMENT POPUP
# =========================================================

# The plus button is placed ABOVE the native chat input,
# but visually designed as part of the same prompt area.

plus_col, prompt_col, mic_col = st.columns(
    [0.8, 7.8, 1.0]
)


# =========================================================
# PLUS BUTTON
# =========================================================

with plus_col:

    st.markdown(
        '<div class="plus-button">',
        unsafe_allow_html=True,
    )

    with st.popover(
        "＋",
        use_container_width=True,
    ):

        st.markdown(
            '<div class="attach-heading">Add to your question</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="attach-subheading">'
            'Attach something to your conversation'
            '</div>',
            unsafe_allow_html=True,
        )


        # -------------------------------------------------
        # PHOTOS
        # -------------------------------------------------

        st.markdown(
            """
            <div class="attach-option">

                <span class="attach-icon">🖼️</span>

                <span class="attach-name">
                    Add photos
                </span>

                <br>

                <span class="attach-desc">
                    Upload images from your computer
                </span>

            </div>
            """,
            unsafe_allow_html=True,
        )

        photos = st.file_uploader(
            "Choose photos",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
                "gif",
            ],
            accept_multiple_files=True,
            key="quantum_photos",
            label_visibility="collapsed",
        )


        # -------------------------------------------------
        # FILES
        # -------------------------------------------------

        st.markdown(
            """
            <div class="attach-option">

                <span class="attach-icon">📄</span>

                <span class="attach-name">
                    Add files
                </span>

                <br>

                <span class="attach-desc">
                    PDF, TXT, DOCX, CSV, Python and more
                </span>

            </div>
            """,
            unsafe_allow_html=True,
        )

        documents = st.file_uploader(
            "Choose files",
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
            key="quantum_documents",
            label_visibility="collapsed",
        )


        # -------------------------------------------------
        # STORE FRONTEND ATTACHMENTS
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
                f"📎 {len(selected_files)} file(s) attached"
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# MICROPHONE
# =========================================================

with mic_col:

    st.markdown(
        '<div class="mic-container">',
        unsafe_allow_html=True,
    )

    audio_value = st.audio_input(
        "🎙️",
        key="quantum_microphone",
        label_visibility="collapsed",
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# PROMPT
# =========================================================

with prompt_col:

    query = st.chat_input(
        "Ask your quantum question..."
    )


# =========================================================
# MICROPHONE → SPEECH → TEXT
# =========================================================

voice_query = None


if audio_value:

    # Prevent processing the exact same recording
    # multiple times during Streamlit reruns.

    audio_bytes = audio_value.getvalue()

    current_audio_id = hash(
        audio_bytes
    )

    if (
        current_audio_id
        != st.session_state.last_audio_id
    ):

        st.session_state.last_audio_id = (
            current_audio_id
        )

        if not SPEECH_RECOGNITION_AVAILABLE:

            st.warning(
                "🎙️ Microphone recording works, "
                "but speech-to-text is not installed yet. "
                "Add SpeechRecognition to requirements.txt."
            )

        else:

            try:

                recognizer = sr.Recognizer()

                audio_file = io.BytesIO(
                    audio_bytes
                )

                with sr.AudioFile(
                    audio_file
                ) as source:

                    recorded_audio = (
                        recognizer.record(source)
                    )

                with st.spinner(
                    "🎙️ Understanding your voice..."
                ):

                    voice_query = (
                        recognizer.recognize_google(
                            recorded_audio
                        )
                    )

                if voice_query:

                    st.toast(
                        f"🎙️ Heard: {voice_query}"
                    )

            except sr.UnknownValueError:

                st.warning(
                    "I couldn't understand the recording. "
                    "Please try speaking again."
                )

            except sr.RequestError:

                st.warning(
                    "Speech recognition service is "
                    "temporarily unavailable."
                )

            except Exception as e:

                st.warning(
                    f"Microphone processing failed: {str(e)}"
                )


# =========================================================
# CHOOSE TEXT OR VOICE QUERY
# =========================================================

final_query = None

if query:

    final_query = query.strip()

elif voice_query:

    final_query = voice_query.strip()


# =========================================================
# PROCESS QUESTION
# =========================================================

if final_query:

    if not final_query:

        st.stop()


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": final_query,
        }
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            final_query
        )

        # Attachments are shown visually only.
        # They are NOT passed into answer_question().

        if st.session_state.uploaded_files:

            st.caption(
                "📎 "
                +
                ", ".join(
                    file.name
                    for file
                    in st.session_state.uploaded_files
                )
            )


    # -----------------------------------------------------
    # EXISTING RAG FUNCTION
    # DO NOT CHANGE
    # -----------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "🔎 Searching the quantum knowledge base..."
        ):

            try:

                # =============================================
                # YOUR EXISTING RAG CALL
                # =============================================

                answer = answer_question(
                    query=final_query,
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
    # SAVE ANSWER TO UI STATE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


    # -----------------------------------------------------
    # CLEAR FRONTEND ATTACHMENTS
    # -----------------------------------------------------

    st.session_state.uploaded_files = []
