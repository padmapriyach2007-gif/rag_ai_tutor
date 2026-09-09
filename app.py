import inspect
import streamlit as st

# ============================================================
# VOICE INPUT
# ============================================================

try:
    from streamlit_mic_recorder import speech_to_text

    VOICE_AVAILABLE = True

except ImportError:
    VOICE_AVAILABLE = False


# ============================================================
# RAG ENGINE
# ============================================================

from rag_engine import (
    answer_question,
    create_chat_session,
    delete_chat,
    get_or_create_user,
    get_user_sessions,
    rename_chat,
    restore_chat,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Lab | AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "logged_in": False,
    "user_email": "",
    "user_id": None,

    "session_id": None,
    "messages": [],

    "sessions": [],
    "sessions_loaded_for_user": None,

    "loaded_session_id": None,

    "prompt_nonce": 0,
    "prompt_seed": "",

    "voice_text": "",
    "last_voice_text": "",

    "rename_session_id": None,

    "show_canvas": False,
    "show_calculator": False,
    "show_learning": False,
    "show_notes": False,

    "notes": "",

    "think_mode": False,

    "pending_question": None,
}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

.stApp {

    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(105, 75, 255, 0.18),
            transparent 28%
        ),

        radial-gradient(
            circle at 90% 15%,
            rgba(0, 190, 255, 0.12),
            transparent 30%
        ),

        radial-gradient(
            circle at 50% 100%,
            rgba(150, 60, 255, 0.10),
            transparent 35%
        ),

        linear-gradient(
            135deg,
            #050510 0%,
            #08091d 48%,
            #061221 100%
        );

    color: #f5f5ff;

}


/* ============================================================
   STAR / GRID EFFECT
   ============================================================ */

.stApp::before {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    opacity: 0.22;

    background-image:

        linear-gradient(
            rgba(120, 100, 255, 0.045) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(120, 100, 255, 0.045) 1px,
            transparent 1px
        );

    background-size: 48px 48px;

}


/* ============================================================
   HEADER
   ============================================================ */

[data-testid="stHeader"] {

    background: transparent !important;

}


/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            rgba(4, 6, 20, 0.98),
            rgba(4, 5, 16, 0.99)
        ) !important;

    border-right:
        1px solid
        rgba(130, 110, 255, 0.18);

}


[data-testid="stSidebar"] > div {

    padding-top: 1rem;

}


/* Sidebar buttons */

[data-testid="stSidebar"] .stButton > button {

    width: 100%;

    min-height: 42px;

    border-radius: 12px;

    background:
        rgba(28, 28, 62, 0.58);

    border:
        1px solid
        rgba(135, 115, 255, 0.20);

    color: #f4f2ff;

    transition:
        all 0.22s ease;

}


[data-testid="stSidebar"] .stButton > button:hover {

    background:
        rgba(65, 55, 120, 0.55);

    border-color:
        rgba(155, 140, 255, 0.55);

    transform:
        translateY(-1px);

    box-shadow:
        0 0 20px
        rgba(120, 100, 255, 0.18);

}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.sidebar-brand {

    text-align: center;

    padding:
        10px 5px 24px;

}


.sidebar-logo {

    width: 58px;

    height: 58px;

    display: flex;

    align-items: center;

    justify-content: center;

    margin:
        0 auto 12px;

    border-radius: 14px;

    font-size: 38px;

    background:
        linear-gradient(
            145deg,
            #855cff,
            #5931ca
        );

    box-shadow:
        0 0 30px
        rgba(115, 80, 255, 0.55);

}


.sidebar-title {

    font-size: 20px;

    font-weight: 850;

    letter-spacing: 1px;

}


.sidebar-subtitle {

    color: #8889ac;

    font-size: 12px;

    margin-top: 5px;

}


/* ============================================================
   MAIN HERO
   ============================================================ */

.hero-box {

    position: relative;

    max-width: 1050px;

    margin:
        28px auto 25px;

    padding:
        45px 25px;

    text-align: center;

    border-radius: 28px;

    background:
        linear-gradient(
            145deg,
            rgba(37, 33, 82, 0.68),
            rgba(9, 13, 32, 0.80)
        );

    border:
        1px solid
        rgba(145, 125, 255, 0.20);

    box-shadow:
        0 25px 80px
        rgba(0, 0, 0, 0.35),

        inset 0 0 35px
        rgba(100, 80, 255, 0.04);

}


.hero-icon {

    font-size: 58px;

    line-height: 1;

    filter:
        drop-shadow(
            0 0 22px
            rgba(140, 110, 255, 0.85)
        );

    animation:
        quantumFloat 4s ease-in-out infinite;

}


@keyframes quantumFloat {

    0%,100% {

        transform:
            translateY(0px);

    }

    50% {

        transform:
            translateY(-6px);

    }

}


.hero-title {

    margin-top: 12px;

    font-size:
        clamp(32px, 5vw, 55px);

    font-weight: 900;

    letter-spacing: -1.5px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #b9adff,
            #84eaff
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;

}


.hero-subtitle {

    margin-top: 8px;

    color: #a7a8c2;

    font-size: 15px;

}


.online {

    display: inline-block;

    margin-top: 18px;

    padding:
        7px 16px;

    border-radius: 30px;

    color: #82efb5;

    background:
        rgba(50, 220, 145, 0.07);

    border:
        1px solid
        rgba(70, 220, 155, 0.25);

    font-size: 11px;

    font-weight: 700;

}


/* ============================================================
   WELCOME CARD
   ============================================================ */

.welcome-card {

    max-width: 850px;

    margin:
        20px auto;

    padding: 28px;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            rgba(32, 29, 70, 0.68),
            rgba(10, 12, 29, 0.78)
        );

    border:
        1px solid
        rgba(130, 110, 255, 0.18);

}


.welcome-title {

    font-size: 22px;

    font-weight: 800;

}


.welcome-text {

    margin-top: 8px;

    color: #aaaac4;

    line-height: 1.65;

    font-size: 14px;

}


/* ============================================================
   CHAT MESSAGES
   ============================================================ */

[data-testid="stChatMessage"] {

    border-radius: 18px;

    margin-bottom: 8px;

}


[data-testid="stChatMessageContent"] {

    font-size: 15px;

    line-height: 1.7;

}


/* ============================================================
   LOGIN
   ============================================================ */

.login-page {

    min-height: 78vh;

    display: flex;

    align-items: center;

    justify-content: center;

}


.login-card {

    width: min(470px, 92vw);

    padding: 42px;

    border-radius: 28px;

    text-align: center;

    background:
        linear-gradient(
            145deg,
            rgba(28, 27, 66, 0.88),
            rgba(8, 12, 29, 0.92)
        );

    border:
        1px solid
        rgba(140, 120, 255, 0.30);

    box-shadow:

        0 30px 100px
        rgba(0, 0, 0, 0.55),

        0 0 55px
        rgba(100, 75, 255, 0.15);

}


.login-logo {

    width: 76px;

    height: 76px;

    margin: 0 auto 20px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 20px;

    font-size: 48px;

    background:
        linear-gradient(
            145deg,
            #855cff,
            #4923b9
        );

    box-shadow:
        0 0 40px
        rgba(120, 80, 255, 0.60);

}


.login-title {

    font-size: 34px;

    font-weight: 900;

}


.login-subtitle {

    color: #999ab8;

    margin:
        8px 0 28px;

    font-size: 14px;

}


/* ============================================================
   PROMPT AREA
   ============================================================ */

.prompt-zone {

    max-width: 1100px;

    margin:
        25px auto 10px;

}


.prompt-row {

    padding:
        7px 10px;

    border-radius: 24px;

    background:
        linear-gradient(
            145deg,
            rgba(25, 24, 55, 0.94),
            rgba(10, 13, 30, 0.96)
        );

    border:
        1px solid
        rgba(130, 115, 255, 0.28);

    box-shadow:
        0 12px 45px
        rgba(0, 0, 0, 0.30);

    transition:
        all 0.25s ease;

}


/* Glow while typing */

[data-testid="stTextInput"]:has(input:focus) {

    border-radius: 18px;

    box-shadow:
        0 0 0 1px
        rgba(130, 105, 255, 0.55),

        0 0 28px
        rgba(105, 75, 255, 0.30);

}


[data-testid="stTextInput"] input {

    height: 46px;

    border-radius: 16px !important;

    background:
        rgba(15, 16, 36, 0.92) !important;

    border:
        1px solid
        rgba(125, 110, 240, 0.16) !important;

    color: white !important;

    font-size: 15px !important;

    padding-left: 16px !important;

}


[data-testid="stTextInput"] input:focus {

    border:
        1px solid
        rgba(130, 110, 255, 0.65) !important;

    box-shadow:
        0 0 20px
        rgba(110, 80, 255, 0.25) !important;

}


/* ============================================================
   PROMPT BUTTONS
   ============================================================ */

.prompt-zone .stButton > button {

    min-height: 46px;

    border-radius: 16px;

    transition:
        all 0.20s ease;

}


.prompt-zone .stButton > button:hover {

    transform:
        translateY(-1px);

}


/* Think */

.think-column .stButton > button {

    background:
        rgba(60, 48, 110, 0.48);

    border:
        1px solid
        rgba(135, 110, 255, 0.25);

    color: #d9d2ff;

}


.think-active .stButton > button {

    background:
        linear-gradient(
            135deg,
            rgba(115, 75, 255, 0.55),
            rgba(55, 135, 255, 0.35)
        ) !important;

    border-color:
        rgba(150, 130, 255, 0.75) !important;

    box-shadow:
        0 0 22px
        rgba(105, 75, 255, 0.30);

}


/* Microphone */

.mic-column {

    display: flex;

    align-items: center;

    justify-content: center;

}


/*
   The speech_to_text component is intentionally clipped
   to a compact microphone area.
*/

[data-testid="stCustomComponentV1"] {

    border: none !important;

}


.mic-column iframe {

    border: none !important;

    border-radius: 50% !important;

}


/* Send */

.send-column .stButton > button {

    width: 48px !important;

    height: 48px !important;

    min-height: 48px !important;

    padding: 0 !important;

    border-radius: 50% !important;

    border:
        1px solid
        rgba(130, 175, 255, 0.60) !important;

    background:
        linear-gradient(
            145deg,
            #4d8dff,
            #5860ff
        ) !important;

    color: white !important;

    font-size: 25px !important;

    font-weight: 800 !important;

    box-shadow:
        0 0 25px
        rgba(70, 110, 255, 0.40);

}


.send-column .stButton > button:hover {

    transform:
        translateY(-2px)
        scale(1.04);

    box-shadow:
        0 0 35px
        rgba(70, 110, 255, 0.65);

}


/* ============================================================
   PLUS POPUP
   ============================================================ */

[data-testid="stPopover"] button {

    border-radius: 15px;

}


/* ============================================================
   TOOL CARDS
   ============================================================ */

.tool-card {

    padding: 18px;

    border-radius: 18px;

    margin-top: 10px;

    background:
        linear-gradient(
            145deg,
            rgba(34, 31, 75, 0.65),
            rgba(10, 13, 31, 0.78)
        );

    border:
        1px solid
        rgba(130, 110, 255, 0.18);

}


.tool-title {

    font-size: 17px;

    font-weight: 800;

    margin-bottom: 8px;

}


.tool-description {

    color: #9d9eb8;

    font-size: 13px;

}


/* ============================================================
   SIDEBAR CARDS
   ============================================================ */

.side-card {

    padding: 15px;

    margin: 12px 0;

    border-radius: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(36, 32, 78, 0.60),
            rgba(12, 14, 32, 0.70)
        );

    border:
        1px solid
        rgba(130, 110, 255, 0.17);

}


.side-card-title {

    font-weight: 750;

    margin-bottom: 7px;

}


.side-card-text {

    color: #999ab4;

    font-size: 12px;

    line-height: 1.55;

}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {

    text-align: center;

    color: #666783;

    font-size: 11px;

    margin-top: 35px;

    padding-bottom: 15px;

}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 800px) {

    .hero-box {

        padding: 32px 18px;

        margin-top: 15px;

    }

    .login-card {

        padding: 30px 22px;

    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def refresh_sessions():
    """Refresh chat list only when explicitly needed."""

    try:

        sessions = get_user_sessions(
            st.session_state.user_id
        )

        st.session_state.sessions = sessions or []

        st.session_state.sessions_loaded_for_user = (
            st.session_state.user_id
        )

    except Exception as e:

        st.session_state.sessions = []

        st.error(
            f"Could not load chats: {e}"
        )


def safe_rename_chat(
    session_id,
    new_title
):
    """
    Supports both:
        rename_chat(session_id, user_id, new_title)
    and:
        rename_chat(session_id, new_title)
    """

    try:

        signature = inspect.signature(rename_chat)

        params = list(
            signature.parameters.values()
        )

        names = [
            p.name
            for p in params
        ]

        # Current rag_engine.py:
        # session_id, user_id, new_title

        if (
            "user_id" in names
            and "new_title" in names
        ):

            return rename_chat(
                session_id,
                st.session_state.user_id,
                new_title
            )

        # Alternative implementation

        if len(params) >= 3:

            return rename_chat(
                session_id,
                st.session_state.user_id,
                new_title
            )

        return rename_chat(
            session_id,
            new_title
        )

    except Exception:

        # Final compatibility fallback

        try:

            return rename_chat(
                session_id,
                st.session_state.user_id,
                new_title
            )

        except TypeError:

            return rename_chat(
                session_id,
                new_title
            )


def safe_delete_chat(session_id):

    try:

        signature = inspect.signature(
            delete_chat
        )

        params = list(
            signature.parameters.values()
        )

        if len(params) >= 2:

            return delete_chat(
                session_id,
                st.session_state.user_id
            )

        return delete_chat(
            session_id
        )

    except TypeError:

        return delete_chat(
            session_id,
            st.session_state.user_id
        )


def load_current_chat():

    session_id = (
        st.session_state.session_id
    )

    if not session_id:
        return

    if (
        st.session_state.loaded_session_id
        == session_id
    ):
        return

    try:

        messages = restore_chat(
            session_id,
            st.session_state.user_id
        )

        st.session_state.messages = (
            messages or []
        )

        st.session_state.loaded_session_id = (
            session_id
        )

    except Exception as e:

        st.error(
            f"Could not load conversation: {e}"
        )

        st.session_state.messages = []

        st.session_state.loaded_session_id = (
            session_id
        )


def start_new_chat():

    try:

        new_session_id = create_chat_session(
            st.session_state.user_id,
            "New Quantum Chat"
        )

        st.session_state.session_id = (
            new_session_id
        )

        st.session_state.messages = []

        st.session_state.loaded_session_id = (
            new_session_id
        )

        refresh_sessions()

        st.toast(
            "✨ New chat created!"
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"Could not create chat: {e}"
        )


def make_chat_title(question):

    """
    Creates a short title from the first question.
    """

    title = question.strip()

    if len(title) > 35:

        title = (
            title[:35].rsplit(" ", 1)[0]
            + "..."
        )

    return title


def auto_update_title(question):

    """
    Automatically rename the first/default chat
    after the first real question.
    """

    try:

        sessions = st.session_state.sessions

        current_id = (
            st.session_state.session_id
        )

        current = None

        for chat in sessions:

            if chat.get("session_id") == current_id:

                current = chat

                break

        if not current:
            return

        current_title = current.get(
            "title",
            ""
        )

        default_titles = {
            "Quantum Learning",
            "New Quantum Chat",
            "New Chat",
            "Untitled Chat",
        }

        if current_title in default_titles:

            new_title = make_chat_title(
                question
            )

            if new_title:

                safe_rename_chat(
                    current_id,
                    new_title
                )

                refresh_sessions()

    except Exception:

        # Title update must never break chat.

        pass


def process_question(question):

    question = question.strip()

    if not question:
        return

    session_id = (
        st.session_state.session_id
    )

    user_id = (
        st.session_state.user_id
    )

    if not session_id:

        st.error(
            "No active chat session."
        )

        return

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    user_message = {
        "sender": "user",
        "content": question
    }

    st.session_state.messages.append(
        user_message
    )

    # --------------------------------------------------------
    # AUTO TITLE
    # --------------------------------------------------------

    if len(st.session_state.messages) == 1:

        auto_update_title(
            question
        )

    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.spinner(
        "🧠 Quantum AI is thinking..."
    ):

        try:

            answer = answer_question(
                query=question,
                session_id=session_id,
                user_id=user_id
            )

        except Exception as e:

            answer = (
                "⚠️ I couldn't process "
                "your question right now.\n\n"
                f"**Error:** `{str(e)}`"
            )

    # --------------------------------------------------------
    # ASSISTANT MESSAGE
    # --------------------------------------------------------

    assistant_message = {
        "sender": "assistant",
        "content": answer
    }

    st.session_state.messages.append(
        assistant_message
    )


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.logged_in:

    # Hide sidebar while logged out

    st.markdown(
        """
<style>
section[data-testid="stSidebar"] {
    display: none !important;
}
</style>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="login-page">

    <div class="login-card">

        <div class="login-logo">
            ⚛️
        </div>

        <div class="login-title">
            Quantum Lab
        </div>

        <div class="login-subtitle">
            AI-Powered Learning Space
        </div>

    </div>

</div>
""",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # LOGIN FORM
    # --------------------------------------------------------

    login_left, login_center, login_right = (
        st.columns([1, 2, 1])
    )

    with login_center:

        st.markdown(
            "### 🔐 Account"
        )

        email = st.text_input(
            "Email",
            placeholder="student@example.com",
            key="login_email"
        )

        if st.button(
            "🔑 Log In",
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

                        session_id = (
                            create_chat_session(
                                user_id,
                                "Quantum Learning"
                            )
                        )

                        sessions = get_user_sessions(
                            user_id
                        )

                    else:

                        session_id = (
                            sessions[0][
                                "session_id"
                            ]
                        )

                    st.session_state.logged_in = True

                    st.session_state.user_email = (
                        email
                    )

                    st.session_state.user_id = (
                        user_id
                    )

                    st.session_state.session_id = (
                        session_id
                    )

                    st.session_state.sessions = (
                        sessions or []
                    )

                    st.session_state.sessions_loaded_for_user = (
                        user_id
                    )

                    st.session_state.loaded_session_id = (
                        None
                    )

                    st.session_state.messages = []

                    st.toast(
                        "✨ Login successful!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Login failed: {e}"
                    )

    st.markdown(
        """
<div class="footer">
    ⚛️ Quantum Lab • AI Tutor
</div>
""",
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        "🔐 **Account**"
    )

    st.caption(
        st.session_state.user_email
    )

    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        start_new_chat()

    # --------------------------------------------------------
    # REFRESH CHAT LIST ONLY WHEN NEEDED
    # --------------------------------------------------------

    if (
        st.session_state.sessions_loaded_for_user
        != st.session_state.user_id
    ):

        refresh_sessions()

    sessions = st.session_state.sessions

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        "### 💬 Your Chats"
    )

    if not sessions:

        st.caption(
            "No chats available."
        )

    for chat in sessions:

        session_id = chat.get(
            "session_id"
        )

        title = chat.get(
            "title",
            "Untitled Chat"
        )

        is_current = (
            session_id
            == st.session_state.session_id
        )

        if is_current:

            label = (
                f"🟣 {title}"
            )

        else:

            label = (
                f"💬 {title}"
            )

        if st.button(
            label,
            key=f"chat_{session_id}",
            use_container_width=True
        ):

            st.session_state.session_id = (
                session_id
            )

            st.session_state.loaded_session_id = (
                None
            )

            st.rerun()

    # --------------------------------------------------------
    # RENAME
    # --------------------------------------------------------

    st.markdown("---")

    with st.expander(
        "✏️ Rename Current Chat"
    ):

        current_chat = None

        for chat in sessions:

            if (
                chat.get("session_id")
                == st.session_state.session_id
            ):

                current_chat = chat

                break

        if current_chat:

            current_title = current_chat.get(
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

                        safe_rename_chat(
                            st.session_state.session_id,
                            new_name
                        )

                        refresh_sessions()

                        st.toast(
                            "✨ Chat renamed!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Rename failed: {e}"
                        )

        else:

            st.info(
                "Select a chat first."
            )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "🗑️ Delete Current Chat",
        use_container_width=True
    ):

        try:

            current_id = (
                st.session_state.session_id
            )

            safe_delete_chat(
                current_id
            )

            refresh_sessions()

            if st.session_state.sessions:

                st.session_state.session_id = (
                    st.session_state.sessions[0][
                        "session_id"
                    ]
                )

            else:

                new_id = create_chat_session(
                    st.session_state.user_id,
                    "Quantum Learning"
                )

                st.session_state.session_id = (
                    new_id
                )

                refresh_sessions()

            st.session_state.loaded_session_id = (
                None
            )

            st.toast(
                "🗑️ Chat deleted!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Delete failed: {e}"
            )

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True
    ):

        try:

            current_id = (
                st.session_state.session_id
            )

            safe_delete_chat(
                current_id
            )

            new_id = create_chat_session(
                st.session_state.user_id,
                "New Quantum Chat"
            )

            st.session_state.session_id = (
                new_id
            )

            st.session_state.messages = []

            st.session_state.loaded_session_id = (
                new_id
            )

            refresh_sessions()

            st.toast(
                "🧹 Conversation cleared!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not clear conversation: {e}"
            )

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user_email = ""

        st.session_state.user_id = None

        st.session_state.session_id = None

        st.session_state.messages = []

        st.session_state.sessions = []

        st.session_state.loaded_session_id = None

        st.rerun()

    # --------------------------------------------------------
    # LEARNING MODE CARD
    # --------------------------------------------------------

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

        ⚛️ Quantum Computing<br>
        🔬 Physics<br>
        💻 Programming<br>
        🧮 Mathematics<br>
        🧠 Artificial Intelligence<br>
        📚 Data Structures<br>
        🌐 General Knowledge

    </div>

</div>


<div class="side-card">

    <div class="side-card-title">
        ✨ AI Tutor
    </div>

    <div class="side-card-text">

        Ask naturally.

        The tutor can explain concepts,
        solve problems, analyze code,
        simplify difficult topics and
        answer general questions.

    </div>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# LOAD CURRENT CHAT
# ============================================================

load_current_chat()


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
        Explore ideas, solve problems and learn through conversation
    </div>

    <div class="online">
        ● AI TUTOR ONLINE
    </div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# WELCOME
# ============================================================

if not st.session_state.messages:

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

        🎙️ You can also use the microphone
        to speak your question.

    </div>

</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        "### 💡 Try asking"
    )

    example_col1, example_col2 = st.columns(2)

    with example_col1:

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

    with example_col2:

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
# DISPLAY CHAT
# ============================================================

for message in st.session_state.messages:

    sender = message.get(
        "sender",
        "assistant"
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
# PLUS POPUP
# ============================================================

st.markdown(
    '<div class="prompt-zone">',
    unsafe_allow_html=True
)


# ============================================================
# PROMPT ROW
# ============================================================

plus_col, prompt_col, think_col, mic_col, send_col = (
    st.columns(
        [0.075, 0.59, 0.13, 0.095, 0.075],
        gap="small"
    )
)


# ============================================================
# PLUS BUTTON / POPUP
# ============================================================

with plus_col:

    with st.popover(
        "＋",
        use_container_width=True
    ):

        st.markdown(
            "### Add to your question"
        )

        tab1, tab2, tab3 = st.tabs(
            [
                "📁 Photos & Files",
                "☁️ Google Drive",
                "🛠️ More Tools"
            ]
        )

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        with tab1:

            uploaded_files = st.file_uploader(
                "Upload files",
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                    "pdf",
                    "txt",
                    "docx",
                    "csv",
                    "xlsx",
                    "py",
                    "java",
                    "c"
                ],
                accept_multiple_files=True,
                key="file_uploader"
            )

            if uploaded_files:

                st.session_state.uploaded_files = [
                    file.name
                    for file in uploaded_files
                ]

                st.success(
                    f"{len(uploaded_files)} file(s) attached."
                )

        # ----------------------------------------------------
        # GOOGLE DRIVE
        # ----------------------------------------------------

        with tab2:

            drive_link = st.text_input(
                "Google Drive link",
                placeholder="Paste Drive file link",
                key="drive_link"
            )

            if st.button(
                "Attach Drive File",
                use_container_width=True
            ):

                if drive_link.strip():

                    st.session_state.drive_links.append(
                        drive_link.strip()
                    )

                    st.success(
                        "☁️ Drive link attached."
                    )

                else:

                    st.warning(
                        "Please enter a Drive link."
                    )

        # ----------------------------------------------------
        # MORE TOOLS
        # ----------------------------------------------------

        with tab3:

            st.markdown(
                "#### 🛠️ Tools"
            )

            tool1, tool2 = st.columns(2)

            with tool1:

                if st.button(
                    "🎨 Canvas",
                    use_container_width=True
                ):

                    st.session_state.show_canvas = True

                if st.button(
                    "📚 Learning Mode",
                    use_container_width=True
                ):

                    st.session_state.show_learning = (
                        not st.session_state.show_learning
                    )

            with tool2:

                if st.button(
                    "🧮 Quantum Calculator",
                    use_container_width=True
                ):

                    st.session_state.show_calculator = True

                if st.button(
                    "📝 Notes",
                    use_container_width=True
                ):

                    st.session_state.show_notes = True


# ============================================================
# VOICE INPUT
# ============================================================

voice_result = None

with mic_col:

    if VOICE_AVAILABLE:

        voice_result = speech_to_text(
            language="en-IN",
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=False,
            key="quantum_voice_input"
        )

    else:

        st.markdown(
            "🎙️"
        )


# ============================================================
# HANDLE VOICE RESULT BEFORE PROMPT WIDGET
# ============================================================

if (
    voice_result
    and voice_result.strip()
):

    voice_result = voice_result.strip()

    # Only process genuinely new recognition result

    if voice_result != st.session_state.last_voice_text:

        st.session_state.last_voice_text = (
            voice_result
        )

        st.session_state.voice_text = (
            voice_result
        )

        # Important:
        # create a NEW prompt widget key.
        #
        # We do NOT do:
        #
        # st.session_state.custom_prompt = ...
        #
        # after the widget has been created.
        #
        # This completely avoids the
        # StreamlitWidgetAlreadyInstantiatedError.

        st.session_state.prompt_seed = (
            voice_result
        )

        st.session_state.prompt_nonce += 1

        st.rerun()


# ============================================================
# PROMPT INPUT
# ============================================================

with prompt_col:

    prompt_key = (
        f"custom_prompt_{st.session_state.prompt_nonce}"
    )

    prompt_value = (
        st.session_state.prompt_seed
    )

    # Consume the seed BEFORE widget creation

    st.session_state.prompt_seed = ""

    user_prompt = st.text_input(
        "Ask anything",
        value=prompt_value,
        placeholder="Ask anything about quantum computing...",
        label_visibility="collapsed",
        key=prompt_key
    )


# ============================================================
# THINK BUTTON
# ============================================================

with think_col:

    think_label = (
        "🧠 Think ON"
        if st.session_state.think_mode
        else "🧠 Think"
    )

    if st.button(
        think_label,
        use_container_width=True
    ):

        st.session_state.think_mode = (
            not st.session_state.think_mode
        )

        st.rerun()


# ============================================================
# SEND BUTTON
# ============================================================

with send_col:

    st.markdown(
        '<div class="send-column-marker"></div>',
        unsafe_allow_html=True
    )

    send_clicked = st.button(
        "↑",
        key="send_question",
        help="Send message"
    )


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# VOICE STATUS
# ============================================================

if (
    st.session_state.voice_text
    and not user_prompt.strip()
):

    st.info(
        "🎙️ Voice recognized. Your text is ready in the prompt."
    )


# ============================================================
# CANVAS
# ============================================================

if st.session_state.show_canvas:

    st.markdown(
        """
<div class="tool-card">

    <div class="tool-title">
        🎨 Quantum Canvas
    </div>

    <div class="tool-description">
        Write ideas, formulas, notes or circuit descriptions.
    </div>

</div>
""",
        unsafe_allow_html=True
    )

    canvas_text = st.text_area(
        "Canvas",
        placeholder="Write or sketch your thoughts here...",
        height=180,
        key="canvas_text"
    )

    canvas_col1, canvas_col2 = st.columns(2)

    with canvas_col1:

        if st.button(
            "💾 Save Canvas",
            use_container_width=True
        ):

            st.toast(
                "Canvas saved for this session."
            )

    with canvas_col2:

        if st.button(
            "✕ Close Canvas",
            use_container_width=True
        ):

            st.session_state.show_canvas = False

            st.rerun()


# ============================================================
# QUANTUM CALCULATOR
# ============================================================

if st.session_state.show_calculator:

    st.markdown(
        """
<div class="tool-card">

    <div class="tool-title">
        🧮 Quantum Calculator
    </div>

    <div class="tool-description">
        Use the AI tutor for quantum formulas,
        probabilities, amplitudes and calculations.
    </div>

</div>
""",
        unsafe_allow_html=True
    )

    calculator_expression = st.text_input(
        "Expression",
        placeholder="Example: 2**3 + 5",
        key="calculator_expression"
    )

    if st.button(
        "Calculate",
        use_container_width=True
    ):

        try:

            # Simple safe calculator

            allowed = set(
                "0123456789+-*/().% "
            )

            if not set(
                calculator_expression
            ).issubset(allowed):

                st.error(
                    "Only basic mathematical operators are allowed."
                )

            else:

                result = eval(
                    calculator_expression,
                    {
                        "__builtins__": {}
                    },
                    {}
                )

                st.success(
                    f"Result: {result}"
                )

        except Exception:

            st.error(
                "Please enter a valid expression."
            )


# ============================================================
# LEARNING MODE
# ============================================================

if st.session_state.show_learning:

    st.markdown(
        """
<div class="tool-card">

    <div class="tool-title">
        📚 Learning Mode
    </div>

    <div class="tool-description">

        Try asking:

        <br><br>

        • Explain this like I'm a beginner<br>
        • Give me an example<br>
        • Quiz me on this topic<br>
        • Give me viva questions<br>
        • Explain step by step<br>
        • Give me exam-important points

    </div>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# NOTES
# ============================================================

if st.session_state.show_notes:

    st.markdown(
        """
<div class="tool-card">

    <div class="tool-title">
        📝 Quick Notes
    </div>

</div>
""",
        unsafe_allow_html=True
    )

    st.session_state.notes = st.text_area(
        "Your notes",
        value=st.session_state.notes,
        height=180,
        placeholder="Write your notes here...",
        key="notes_area"
    )


# ============================================================
# EXAMPLE / PENDING QUESTION
# ============================================================

if st.session_state.pending_question:

    question = (
        st.session_state.pending_question
    )

    st.session_state.pending_question = None

    process_question(
        question
    )

    st.session_state.prompt_nonce += 1

    st.session_state.voice_text = ""

    st.session_state.last_voice_text = ""

    st.rerun()


# ============================================================
# SEND QUESTION
# ============================================================

final_question = ""

if send_clicked:

    final_question = (
        user_prompt.strip()
    )

elif user_prompt.strip():

    # Enter can submit the text input

    # Streamlit reruns when Enter is pressed.

    # We intentionally don't automatically submit
    # on every rerun caused by other controls.

    pass


if final_question:

    process_question(
        final_question
    )

    # Clear prompt safely by changing widget key

    st.session_state.prompt_nonce += 1

    st.session_state.voice_text = ""

    st.session_state.last_voice_text = ""

    st.session_state.prompt_seed = ""

    st.rerun()


# ============================================================
# VOICE HELP
# ============================================================

if not VOICE_AVAILABLE:

    st.warning(
        "🎙️ Voice input requires "
        "`streamlit-mic-recorder`. "
        "Run: `python -m pip install streamlit-mic-recorder`"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">

    ⚛️ Quantum Lab AI Tutor
    • Learn • Explore • Solve

</div>
""",
    unsafe_allow_html=True
)
