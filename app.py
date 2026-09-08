import streamlit as st
from groq import Groq
import os

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Quantum Lab",
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

if "chats" not in st.session_state:
    st.session_state.chats = {
        "Quantum Learning": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Quantum Learning"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

html, body {
    font-family: "Inter", "Segoe UI", sans-serif;
}

.stApp {

    background:
        radial-gradient(
            circle at 10% 15%,
            rgba(89, 70, 255, 0.18),
            transparent 27%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(0, 153, 255, 0.14),
            transparent 30%
        ),
        radial-gradient(
            circle at 50% 100%,
            rgba(130, 55, 255, 0.12),
            transparent 35%
        ),
        #050716;

    color: #ffffff;
}

[data-testid="stMain"] {
    background: transparent;
}


/* ============================================================
   QUANTUM GRID
   ============================================================ */

.stApp::before {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(100, 110, 255, 0.035) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(100, 110, 255, 0.035) 1px,
            transparent 1px
        );

    background-size: 32px 32px;

    opacity: 0.8;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {

    background:
        radial-gradient(
            circle at 20% 5%,
            rgba(100, 80, 255, 0.15),
            transparent 25%
        ),
        radial-gradient(
            circle at 90% 80%,
            rgba(0, 130, 255, 0.08),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            #030511 0%,
            #070a1c 50%,
            #030510 100%
        ) !important;

    border-right:
        1px solid rgba(100, 105, 190, 0.20);
}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.quantum-brand {

    display: flex;

    align-items: center;

    gap: 12px;

    padding: 5px 0 10px 0;
}


.brand-icon {

    width: 43px;
    height: 43px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 12px;

    background:
        linear-gradient(
            135deg,
            #7658ff,
            #397cff
        );

    border:
        1px solid rgba(190, 180, 255, 0.60);

    color: white;

    font-size: 25px;

    box-shadow:
        0 0 25px rgba(90, 70, 255, 0.42);

    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease;
}


.brand-icon:hover {

    transform:
        rotate(8deg)
        scale(1.08);

    box-shadow:
        0 0 35px rgba(100, 80, 255, 0.65);
}


.brand-title {

    color: #ffffff;

    font-size: 19px;

    font-weight: 850;

    letter-spacing: 0.5px;
}


.brand-subtitle {

    color: #737b9b;

    font-size: 11px;

    margin-top: 3px;
}


/* ============================================================
   SIDEBAR DIVIDERS
   ============================================================ */

.side-divider {

    height: 1px;

    margin: 18px 0;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(120, 115, 190, 0.24),
            transparent
        );
}


/* ============================================================
   SIDEBAR LABELS
   ============================================================ */

.section-label,
.section-title {

    color: #dce1f4;

    font-size: 14px;

    font-weight: 700;

    margin-bottom: 9px;
}


/* ============================================================
   USER EMAIL
   ============================================================ */

.user-email {

    color: #4d9eff;

    font-size: 12px;

    padding: 5px 0;

    word-break: break-word;

    transition:
        color 0.25s ease;
}


.user-email:hover {
    color: #82bdff;
}


/* ============================================================
   SIDEBAR BUTTONS
   ============================================================ */

[data-testid="stSidebar"] .stButton > button {

    width: 100%;

    min-height: 43px;

    border-radius: 11px;

    background:
        linear-gradient(
            135deg,
            rgba(20, 24, 52, 0.92),
            rgba(10, 14, 34, 0.92)
        );

    border:
        1px solid rgba(105, 105, 170, 0.25);

    color: #c3c8df;

    font-size: 13px;

    font-weight: 600;

    transition:
        transform 0.25s ease,
        background 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        color 0.25s ease;
}


[data-testid="stSidebar"] .stButton > button:hover {

    transform:
        translateX(4px);

    background:
        linear-gradient(
            100deg,
            rgba(78, 63, 175, 0.90),
            rgba(31, 73, 145, 0.90)
        );

    border-color:
        rgba(120, 110, 255, 0.65);

    color: #ffffff;

    box-shadow:
        0 8px 24px rgba(65, 70, 190, 0.25);
}


[data-testid="stSidebar"] .stButton > button:active {

    transform:
        translateX(2px)
        scale(0.97);
}


[data-testid="stSidebar"] .stButton {
    margin-bottom: 6px;
}


/* ============================================================
   NEW CHAT BUTTON
   ============================================================ */

[data-testid="stSidebar"] .stButton > button {

    overflow: hidden;
}


/* ============================================================
   EXPANDER
   ============================================================ */

[data-testid="stSidebar"] [data-testid="stExpander"] {

    background:
        rgba(10, 14, 35, 0.75) !important;

    border:
        1px solid rgba(105, 105, 170, 0.30) !important;

    border-radius: 12px !important;

    transition:
        border-color 0.25s ease,
        box-shadow 0.25s ease;
}


[data-testid="stSidebar"] [data-testid="stExpander"]:hover {

    border-color:
        rgba(115, 105, 255, 0.60) !important;

    box-shadow:
        0 0 20px rgba(75, 65, 200, 0.12);
}


/* ============================================================
   LEARNING MODE CARD
   ============================================================ */

.learning-card {

    position: relative;

    overflow: hidden;

    padding: 17px;

    border-radius: 17px;

    background:
        linear-gradient(
            145deg,
            rgba(25, 62, 105, 0.97),
            rgba(8, 28, 58, 0.97)
        );

    border:
        1px solid rgba(72, 151, 255, 0.42);

    box-shadow:
        0 12px 30px rgba(0, 0, 0, 0.30),
        inset 0 1px 0 rgba(255,255,255,0.05);

    transition:
        transform 0.3s ease,
        border-color 0.3s ease,
        box-shadow 0.3s ease;
}


.learning-card:hover {

    transform:
        translateY(-3px);

    border-color:
        rgba(90, 170, 255, 0.72);

    box-shadow:
        0 18px 40px rgba(0, 0, 0, 0.40),
        0 0 30px rgba(50, 130, 255, 0.15);
}


/* Decorative glow */

.learning-card::before {

    content: "";

    position: absolute;

    width: 170px;
    height: 170px;

    right: -85px;
    top: -85px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(80, 160, 255, 0.25),
            transparent 70%
        );

    pointer-events: none;
}


/* ============================================================
   LEARNING HEADER
   ============================================================ */

.learning-header {

    display: flex;

    align-items: center;

    gap: 10px;

    margin-bottom: 15px;
}


.learning-icon {

    width: 38px;
    height: 38px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 11px;

    background:
        rgba(110, 85, 255, 0.18);

    border:
        1px solid rgba(150, 130, 255, 0.30);

    font-size: 19px;

    box-shadow:
        0 0 15px rgba(100, 80, 255, 0.15);
}


.learning-title {

    color: white;

    font-size: 15px;

    font-weight: 800;
}


.learning-status {

    color: #63baff;

    font-size: 8px;

    font-weight: 700;

    letter-spacing: 1px;

    margin-top: 2px;
}


.learning-question {

    color: #cbd5ec;

    font-size: 12px;

    margin-bottom: 10px;
}


/* ============================================================
   LEARNING TOPICS
   ============================================================ */

.learning-topic {

    display: flex;

    align-items: center;

    gap: 8px;

    padding: 8px 9px;

    margin-bottom: 6px;

    border-radius: 9px;

    background:
        rgba(255,255,255,0.035);

    border:
        1px solid rgba(255,255,255,0.035);

    color: #d6e2f7;

    font-size: 12px;

    transition:
        transform 0.22s ease,
        background 0.22s ease,
        border-color 0.22s ease;
}


.learning-topic:hover {

    transform:
        translateX(5px);

    background:
        rgba(80, 160, 255, 0.12);

    border-color:
        rgba(100, 175, 255, 0.25);
}


/* ============================================================
   QUANTUM DOTS
   ============================================================ */

.quantum-dots {

    display: flex;

    justify-content: center;

    gap: 5px;

    margin-top: 13px;
}


.quantum-dots span {

    width: 5px;
    height: 5px;

    border-radius: 50%;

    background: #70c5ff;

    box-shadow:
        0 0 8px rgba(80, 180, 255, 0.8);

    animation:
        quantumPulse 1.4s infinite ease-in-out;
}


.quantum-dots span:nth-child(2) {
    animation-delay: 0.15s;
}

.quantum-dots span:nth-child(3) {
    animation-delay: 0.30s;
}

.quantum-dots span:nth-child(4) {
    animation-delay: 0.45s;
}


@keyframes quantumPulse {

    0%,
    100% {

        opacity: 0.25;

        transform:
            scale(0.7);
    }

    50% {

        opacity: 1;

        transform:
            scale(1.3);
    }
}


/* ============================================================
   MAIN HERO
   ============================================================ */

.hero-box {

    width: min(850px, 90%);

    margin: 35px auto 28px auto;

    padding: 38px 30px;

    background:
        linear-gradient(
            145deg,
            rgba(22, 25, 55, 0.92),
            rgba(9, 12, 30, 0.92)
        );

    border:
        1px solid rgba(105, 100, 220, 0.32);

    border-radius: 20px;

    text-align: center;

    box-shadow:
        0 15px 45px rgba(0,0,0,0.30);
}


.hero-icon {

    font-size: 45px;

    margin-bottom: 5px;
}


.hero-title {

    font-size: 38px;

    font-weight: 800;

    color: white;

    letter-spacing: -0.5px;
}


.hero-subtitle {

    font-size: 15px;

    color: #929ab8;

    margin-top: 7px;
}


.online {

    margin-top: 13px;

    color: #43e89a;

    font-size: 12px;

    font-weight: 700;

    letter-spacing: 1px;
}


/* ============================================================
   CHAT MESSAGES
   ============================================================ */

[data-testid="stChatMessage"] {

    border-radius: 15px;

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}


[data-testid="stChatMessage"]:hover {

    transform:
        translateY(-1px);

    box-shadow:
        0 5px 20px rgba(0,0,0,0.12);
}


/* ============================================================
   CHAT INPUT
   ============================================================ */

[data-testid="stChatInput"] {

    border-radius: 16px;
}


[data-testid="stChatInput"] textarea {

    border-radius: 14px !important;

    background:
        rgba(10, 13, 32, 0.92) !important;

    border:
        1px solid rgba(105, 105, 170, 0.35) !important;

    color: white !important;

    transition:
        border-color 0.25s ease,
        box-shadow 0.25s ease;
}


[data-testid="stChatInput"] textarea:focus {

    border-color:
        rgba(115, 105, 255, 0.70) !important;

    box-shadow:
        0 0 25px rgba(85, 70, 255, 0.15) !important;
}


/* ============================================================
   LOGIN CARD
   ============================================================ */

.login-container {

    width: min(440px, 90vw);

    margin: 7vh auto 0 auto;

    padding: 36px 38px 34px 38px;

    background:
        linear-gradient(
            145deg,
            rgba(22, 26, 58, 0.97),
            rgba(8, 11, 29, 0.97)
        );

    border:
        1px solid rgba(110, 105, 255, 0.45);

    border-radius: 24px;

    text-align: center;

    position: relative;

    overflow: hidden;

    box-shadow:
        0 25px 70px rgba(0,0,0,0.45),
        0 0 55px rgba(75,65,255,0.12),
        inset 0 1px 0 rgba(255,255,255,0.07);
}


/* Login glow */

.login-container::before {

    content: "";

    position: absolute;

    width: 300px;
    height: 300px;

    left: 50%;
    top: -210px;

    transform:
        translateX(-50%);

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(100,80,255,0.35),
            transparent 70%
        );

    pointer-events: none;
}


.login-icon {

    width: 70px;
    height: 70px;

    margin: 0 auto 17px auto;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            #795cff,
            #3979ff
        );

    border:
        1px solid rgba(190,180,255,0.65);

    font-size: 37px;

    color: white;

    box-shadow:
        0 0 35px rgba(95,75,255,0.45);

    animation:
        quantumFloat 3s ease-in-out infinite;
}


.login-title {

    color: white;

    font-size: 31px;

    font-weight: 800;

    margin: 0;
}


.login-subtitle {

    color: #8e96b5;

    font-size: 13px;

    margin-top: 7px;

    margin-bottom: 20px;
}


/* ============================================================
   INPUT
   ============================================================ */

[data-testid="stTextInput"] label {

    color: #d5daf0 !important;

    font-size: 13px !important;

    font-weight: 600 !important;
}


[data-testid="stTextInput"] input {

    height: 48px !important;

    border-radius: 12px !important;

    background:
        rgba(5,8,24,0.90) !important;

    border:
        1px solid rgba(110,115,165,0.35) !important;

    color: white !important;

    transition:
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        background 0.25s ease !important;
}


[data-testid="stTextInput"] input:focus {

    border-color:
        #7165ff !important;

    box-shadow:
        0 0 0 3px rgba(100,85,255,0.15),
        0 0 25px rgba(90,75,255,0.10) !important;
}


/* ============================================================
   LOGIN BUTTON
   ============================================================ */

.login-button-space {

    margin-top: 8px;
}


.stButton > button {

    min-height: 46px;

    border-radius: 12px;

    background:
        linear-gradient(
            100deg,
            #5748d9,
            #386fe0
        );

    border:
        1px solid rgba(140,125,255,0.55);

    color: white;

    font-weight: 700;

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease,
        filter 0.25s ease;
}


.stButton > button:hover {

    transform:
        translateY(-2px);

    filter:
        brightness(1.08);

    box-shadow:
        0 12px 32px rgba(65,75,220,0.40);
}


.stButton > button:active {

    transform:
        translateY(1px)
        scale(0.98);
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 768px) {

    .login-container {

        width: 88vw;

        margin-top: 5vh;

        padding: 30px 24px;
    }

    .login-title {

        font-size: 27px;
    }

    .hero-box {

        width: 92%;

        padding: 30px 20px;
    }

    .hero-title {

        font-size: 30px;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# QUANTUM AI RESPONSE
# ============================================================

def ai_response(chat_history):

    # Get Groq API key
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return (
            "⚠️ **Groq API key is missing.**\n\n"
            "Please set your `GROQ_API_KEY` environment variable."
        )

    # Create Groq client
    client = Groq(
        api_key=api_key
    )

    # System instructions
    system_message = {
        "role": "system",
        "content": """
You are a helpful, intelligent AI assistant.

You can answer questions about any subject, including:
science, mathematics, programming, technology, education,
history, general knowledge, writing, and everyday questions.

Do not restrict yourself strictly to quantum computing.

Explain things clearly and adapt your answer to the user's level.

If the user asks for code, provide working code and explain it.

If the user asks a conceptual question, explain it with examples.

If the question is unclear, ask a useful clarification.
"""
    }

    # Combine system message and conversation history
    full_messages = [system_message] + chat_history

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=full_messages
        )

        return response.choices[0].message.content

    except Exception as e:

        return (
            "⚠️ **Sorry, I could not generate a response right now.**\n\n"
            f"Error details: `{str(e)}`"
        )


def answer_question(question, chat_history):
    return ai_response(chat_history)


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.logged_in:

    # --------------------------------------------------------
    # LOGIN CARD
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="login-container">

            <div class="login-icon">
                ⚛️
            </div>

            <div class="login-title">
                Quantum Lab
            </div>

            <div class="login-subtitle">
                AI-Powered Learning Space
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # LOGIN FORM
    # --------------------------------------------------------

    email = st.text_input(
        "Email address",
        placeholder="Enter your email"
    )


    if st.button(
        "🚀  Login",
        use_container_width=True
    ):

        if email.strip() == "":

            st.error(
                "Please enter your email address."
            )

        else:

            st.session_state.user_email = email.strip()

            st.session_state.logged_in = True

            st.success(
                "Login successful!"
            )

            st.rerun()


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
        <div class="quantum-brand">

            <div class="brand-icon">
                ⚛
            </div>

            <div>

                <div class="brand-title">
                    QUANTUM LAB
                </div>

                <div class="brand-subtitle">
                    AI-Powered Learning Space
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    st.markdown(
        '<div class="side-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-label">
            👤 &nbsp; Logged In
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="user-email">
            {st.session_state.user_email}
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    st.markdown(
        '<div class="side-divider"></div>',
        unsafe_allow_html=True
    )

    if st.button(
        "✚  New Chat",
        use_container_width=True
    ):

        chat_number = 1

        while f"New Quantum Chat {chat_number}" in st.session_state.chats:

            chat_number += 1

        new_chat_name = (
            f"New Quantum Chat {chat_number}"
        )

        st.session_state.chats[new_chat_name] = []

        st.session_state.current_chat = new_chat_name

        st.toast(
            "New chat created!"
        )

        st.rerun()


    # --------------------------------------------------------
    # YOUR CHATS
    # --------------------------------------------------------

    st.markdown(
        '<div class="side-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-title">
            💬 &nbsp; Your Chats
        </div>
        """,
        unsafe_allow_html=True
    )


    chat_names = list(
        st.session_state.chats.keys()
    )


    for chat_name in chat_names:

        is_current = (
            chat_name ==
            st.session_state.current_chat
        )


        button_text = (

            f"🟣  {chat_name}"

            if is_current

            else

            f"◉  {chat_name}"
        )


        if st.button(
            button_text,
            key=f"open_{chat_name}",
            use_container_width=True
        ):

            st.session_state.current_chat = chat_name

            st.rerun()


    # --------------------------------------------------------
    # RENAME CHAT
    # --------------------------------------------------------

    st.markdown(
        '<div class="side-divider"></div>',
        unsafe_allow_html=True
    )


    with st.expander(
        "✏️  Rename Current Chat"
    ):

        current_name = (
            st.session_state.current_chat
        )


        new_name = st.text_input(
            "New chat name",
            value=current_name,
            key="rename_input"
        )


        if st.button(
            "Save New Name",
            use_container_width=True
        ):

            new_name = new_name.strip()


            if new_name == "":

                st.error(
                    "Chat name cannot be empty."
                )


            elif new_name == current_name:

                st.info(
                    "This is already the current name."
                )


            elif new_name in st.session_state.chats:

                st.error(
                    "A chat with this name already exists."
                )


            else:

                st.session_state.chats[new_name] = (
                    st.session_state.chats.pop(
                        current_name
                    )
                )

                st.session_state.current_chat = new_name

                st.success(
                    "Chat renamed!"
                )

                st.rerun()


    # --------------------------------------------------------
    # DELETE CURRENT CHAT
    # --------------------------------------------------------

    st.markdown(
        '<div class="side-divider"></div>',
        unsafe_allow_html=True
    )


    if st.button(
        "🗑️  Delete Current Chat",
        use_container_width=True
    ):

        current_name = (
            st.session_state.current_chat
        )


        if len(st.session_state.chats) == 1:

            st.session_state.chats[current_name] = []

            st.toast(
                "Chat cleared!"
            )


        else:

            del st.session_state.chats[current_name]

            remaining_chats = list(
                st.session_state.chats.keys()
            )

            st.session_state.current_chat = (
                remaining_chats[0]
            )

            st.toast(
                "Chat deleted!"
            )


        st.rerun()


    # --------------------------------------------------------
    # CLEAR CONVERSATION
    # --------------------------------------------------------

    if st.button(
        "🧹  Clear Conversation",
        use_container_width=True
    ):

        current_name = (
            st.session_state.current_chat
        )

        st.session_state.chats[current_name] = []

        st.toast(
            "Conversation cleared!"
        )

        st.rerun()


    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "🚪  Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.rerun()


    # --------------------------------------------------------
    # LEARNING MODE
    # --------------------------------------------------------

    st.markdown(
        '<div class="side-divider"></div>',
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="learning-card">

            <div class="learning-header">

                <div class="learning-icon">
                    🧠
                </div>

                <div>

                    <div class="learning-title">
                        Learning Mode
                    </div>

                    <div class="learning-status">
                        QUANTUM KNOWLEDGE
                    </div>

                </div>

            </div>


            <div class="learning-question">
                Ask questions about:
            </div>


            <div class="learning-topic">
                <span>⚛️</span>
                Quantum Computing
            </div>


            <div class="learning-topic">
                <span>🔵</span>
                Qubits
            </div>


            <div class="learning-topic">
                <span>〰️</span>
                Quantum Gates
            </div>


            <div class="learning-topic">
                <span>🧪</span>
                Qiskit
            </div>


            <div class="quantum-dots">

                <span></span>
                <span></span>
                <span></span>
                <span></span>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN AREA
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

current_chat = (
    st.session_state.current_chat
)

messages = (
    st.session_state.chats[current_chat]
)


# ============================================================
# DISPLAY CHAT
# ============================================================

for message in messages:

    if message["role"] == "user":

        with st.chat_message("user"):

            st.markdown(
                message["content"]
            )

    else:

        with st.chat_message("assistant"):

            st.markdown(
                message["content"]
            )


# ============================================================
# CHAT INPUT & LOGIC
# ============================================================

question = st.chat_input(
    "Ask anything about quantum computing..."
)


if question:

    # --------------------------------------------------------
    # APPEND USER MESSAGE
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------------
    # RENDER USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # --------------------------------------------------------
    # GENERATE RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = answer_question(
                question,
                messages
            )

            st.markdown(answer)


    # --------------------------------------------------------
    # APPEND AI RESPONSE
    # --------------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # --------------------------------------------------------
    # SAVE UPDATED STATE
    # --------------------------------------------------------

    st.session_state.chats[current_chat] = messages


    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    st.rerun()
