import os
import streamlit as st
from groq import Groq

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
# GALAXY THEME CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   IMPORT FONT
   ============================================================ */

@import url(
    'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap'
);


/* ============================================================
   GLOBAL
   ============================================================ */

html, body {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 20%,
            rgba(108, 63, 255, 0.18),
            transparent 25%
        ),
        radial-gradient(
            circle at 85% 15%,
            rgba(0, 157, 255, 0.16),
            transparent 28%
        ),
        radial-gradient(
            circle at 50% 80%,
            rgba(168, 52, 255, 0.13),
            transparent 32%
        ),
        linear-gradient(
            135deg,
            #02030d,
            #070b20,
            #030716
        );
    color: #ffffff;
}


/* ============================================================
   GALAXY STAR FIELD
   ============================================================ */

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        radial-gradient(
            1px 1px at 10% 20%,
            rgba(255,255,255,0.8),
            transparent
        ),
        radial-gradient(
            1px 1px at 20% 80%,
            rgba(160,190,255,0.8),
            transparent
        ),
        radial-gradient(
            1px 1px at 35% 35%,
            rgba(255,255,255,0.7),
            transparent
        ),
        radial-gradient(
            1px 1px at 50% 15%,
            rgba(170,120,255,0.8),
            transparent
        ),
        radial-gradient(
            1px 1px at 65% 70%,
            rgba(255,255,255,0.7),
            transparent
        ),
        radial-gradient(
            1px 1px at 80% 40%,
            rgba(100,180,255,0.8),
            transparent
        ),
        radial-gradient(
            2px 2px at 90% 85%,
            rgba(255,255,255,0.9),
            transparent
        );
    background-size: 250px 250px;
    opacity: 0.7;
    animation: starsMove 25s linear infinite;
}


@keyframes starsMove {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
    100% { transform: translateY(0px); }
}


/* ============================================================
   SUBTLE GRID
   ============================================================ */

.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(
            rgba(90, 90, 180, 0.025) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(90, 90, 180, 0.025) 1px,
            transparent 1px
        );
    background-size: 35px 35px;
}


/* ============================================================
   MAIN AREA
   ============================================================ */

[data-testid="stMain"] {
    background: transparent;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 30% 5%,
            rgba(105, 65, 255, 0.18),
            transparent 30%
        ),
        radial-gradient(
            circle at 80% 75%,
            rgba(0, 150, 255, 0.10),
            transparent 35%
        ),
        linear-gradient(
            180deg,
            #03040e,
            #070a1c,
            #02030b
        ) !important;
    border-right: 1px solid rgba(120, 105, 255, 0.25);
}


/* ============================================================
   BRAND
   ============================================================ */

.quantum-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 5px 0 10px 0;
}


.brand-icon {
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: linear-gradient(135deg, #8b5cff, #397dff);
    border: 1px solid rgba(210,190,255,0.6);
    font-size: 25px;
    color: white;
    box-shadow: 0 0 20px rgba(117, 75, 255, 0.55), 0 0 45px rgba(45, 120, 255, 0.25);
    animation: iconPulse 3s ease-in-out infinite;
}


@keyframes iconPulse {
    0%, 100% {
        box-shadow: 0 0 20px rgba(117,75,255,0.45), 0 0 40px rgba(45,120,255,0.15);
    }
    50% {
        box-shadow: 0 0 30px rgba(117,75,255,0.75), 0 0 60px rgba(45,120,255,0.30);
    }
}


.brand-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #ffffff, #bca8ff, #72b9ff, #ffffff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: galaxyText 5s linear infinite;
}


.brand-subtitle {
    color: #737b9c;
    font-size: 10px;
    margin-top: 4px;
    letter-spacing: 0.5px;
}


@keyframes galaxyText {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}


/* ============================================================
   SIDEBAR DIVIDER
   ============================================================ */

.side-divider {
    height: 1px;
    margin: 18px 0;
    background: linear-gradient(90deg, transparent, rgba(120,100,255,0.35), rgba(40,150,255,0.25), transparent);
}


/* ============================================================
   SIDEBAR TITLES
   ============================================================ */

.section-label,
.section-title {
    font-family: 'Orbitron', sans-serif;
    color: #dfe5ff;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
}


/* ============================================================
   EMAIL
   ============================================================ */

.user-email {
    color: #65aaff;
    font-size: 12px;
    margin-top: 7px;
    text-shadow: 0 0 10px rgba(60,140,255,0.35);
    transition: all 0.3s ease;
}


.user-email:hover {
    color: #b19aff;
    text-shadow: 0 0 15px rgba(120,80,255,0.7);
}


/* ============================================================
   SIDEBAR BUTTONS
   ============================================================ */

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(18,21,48,0.90), rgba(8,11,30,0.95));
    border: 1px solid rgba(105,105,180,0.28);
    color: #bfc6e5;
    font-size: 12px;
    font-weight: 600;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
}


[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateX(5px);
    background: linear-gradient(100deg, rgba(77,55,180,0.85), rgba(27,82,160,0.85));
    border-color: rgba(130,115,255,0.8);
    color: #ffffff;
    box-shadow: 0 8px 25px rgba(70,60,200,0.3), 0 0 18px rgba(90,70,255,0.12);
}


[data-testid="stSidebar"] .stButton > button:active {
    transform: scale(0.96);
}


/* ============================================================
   EXPANDER
   ============================================================ */

[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(7,10,29,0.8) !important;
    border: 1px solid rgba(110,105,190,0.3) !important;
    border-radius: 12px !important;
}


[data-testid="stSidebar"] [data-testid="stExpander"]:hover {
    border-color: rgba(130,110,255,0.7) !important;
    box-shadow: 0 0 25px rgba(80,65,220,0.15);
}


/* ============================================================
   LEARNING MODE
   ============================================================ */

.learning-card {
    position: relative;
    overflow: hidden;
    padding: 18px;
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(25,55,105,0.96), rgba(8,22,52,0.96));
    border: 1px solid rgba(76,150,255,0.45);
    box-shadow: 0 15px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06);
    transition: all 0.35s ease;
}


.learning-card:hover {
    transform: translateY(-4px);
    border-color: rgba(90,170,255,0.85);
    box-shadow: 0 20px 45px rgba(0,0,0,0.45), 0 0 30px rgba(50,130,255,0.16);
}


.learning-card::before {
    content: "";
    position: absolute;
    width: 200px;
    height: 200px;
    right: -100px;
    top: -100px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(100,150,255,0.30), transparent 70%);
}


.learning-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}


.learning-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: rgba(125,90,255,0.2);
    border: 1px solid rgba(160,135,255,0.35);
    font-size: 20px;
    box-shadow: 0 0 18px rgba(100,80,255,0.2);
}


.learning-title {
    font-family: 'Orbitron', sans-serif;
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.5px;
}


.learning-status {
    color: #61b8ff;
    font-size: 7px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-top: 3px;
}


.learning-question {
    color: #b9c8e5;
    font-size: 12px;
    margin-bottom: 10px;
}


.learning-topic {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 9px;
    margin-bottom: 7px;
    border-radius: 10px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.04);
    color: #d9e4f8;
    font-size: 11px;
    transition: all 0.25s ease;
}


.learning-topic:hover {
    transform: translateX(6px);
    background: rgba(90,160,255,0.13);
    border-color: rgba(100,170,255,0.28);
    color: white;
}


/* ============================================================
   MAIN HERO
   ============================================================ */

.hero-box {
    width: min(820px, 92%);
    margin: 45px auto 30px auto;
    padding: 42px 30px;
    position: relative;
    overflow: hidden;
    text-align: center;
    border-radius: 24px;
    background: linear-gradient(145deg, rgba(20,24,58,0.88), rgba(7,10,28,0.90));
    border: 1px solid rgba(110,100,230,0.38);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 50px rgba(75,60,255,0.10);
}


.hero-box::before {
    content: "";
    position: absolute;
    width: 500px;
    height: 180px;
    left: 50%;
    top: -130px;
    transform: translateX(-50%);
    border-radius: 50%;
    background: radial-gradient(ellipse, rgba(112,76,255,0.38), transparent 70%);
}


.hero-icon {
    position: relative;
    font-size: 48px;
    text-shadow: 0 0 12px rgba(150,120,255,0.9), 0 0 35px rgba(75,100,255,0.7);
}


.hero-title {
    position: relative;
    font-family: 'Orbitron', sans-serif;
    font-size: 38px;
    font-weight: 900;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #ffffff, #a889ff, #5ebaff, #ffffff, #a889ff);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: galaxyTitle 6s linear infinite;
    text-shadow: 0 0 25px rgba(110,80,255,0.15);
}


@keyframes galaxyTitle {
    0% { background-position: 0% center; }
    100% { background-position: 300% center; }
}


.hero-subtitle {
    position: relative;
    color: #929cbc;
    font-size: 14px;
    margin-top: 9px;
    letter-spacing: 0.3px;
}


.online {
    position: relative;
    margin-top: 15px;
    color: #4cf0a0;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    text-shadow: 0 0 12px rgba(60,240,150,0.55);
}


/* ============================================================
   LOGIN CARD
   ============================================================ */

.login-container {
    width: min(460px, 90vw);
    margin: 7vh auto 22px auto;
    padding: 38px 40px;
    position: relative;
    overflow: hidden;
    text-align: center;
    border-radius: 25px;
    background: radial-gradient(circle at 50% 0%, rgba(100,70,255,0.15), transparent 45%), linear-gradient(145deg, rgba(22,26,60,0.96), rgba(6,9,26,0.98));
    border: 1px solid rgba(120,105,255,0.50);
    box-shadow: 0 25px 80px rgba(0,0,0,0.50), 0 0 50px rgba(80,60,255,0.13), inset 0 1px 0 rgba(255,255,255,0.08);
}


.login-container::before {
    content: "";
    position: absolute;
    width: 300px;
    height: 300px;
    left: 50%;
    top: -220px;
    transform: translateX(-50%);
    border-radius: 50%;
    background: radial-gradient(circle, rgba(120,80,255,0.4), transparent 70%);
}


.login-icon {
    position: relative;
    width: 72px;
    height: 72px;
    margin: 0 auto 18px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    background: linear-gradient(135deg, #805dff, #367eff);
    border: 1px solid rgba(210,195,255,0.7);
    font-size: 38px;
    box-shadow: 0 0 25px rgba(110,75,255,0.55), 0 0 55px rgba(40,110,255,0.25);
    animation: loginFloat 3s ease-in-out infinite;
}


@keyframes loginFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}


.login-title {
    position: relative;
    font-family: 'Orbitron', sans-serif;
    font-size: 30px;
    font-weight: 900;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #ffffff, #b59cff, #67bfff, #ffffff);
    background-size: 250% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: galaxyTitle 5s linear infinite;
}


.login-subtitle {
    position: relative;
    color: #858eae;
    font-size: 13px;
    margin-top: 6px;
}


/* ============================================================
   INPUT
   ============================================================ */

[data-testid="stTextInput"] label {
    color: #cdd4ed !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}


[data-testid="stTextInput"] input {
    height: 48px !important;
    border-radius: 12px !important;
    background: rgba(4,7,22,0.92) !important;
    border: 1px solid rgba(105,105,170,0.35) !important;
    color: white !important;
    transition: all 0.3s ease !important;
}


[data-testid="stTextInput"] input:focus {
    border-color: #7867ff !important;
    box-shadow: 0 0 0 3px rgba(105,85,255,0.13), 0 0 25px rgba(90,70,255,0.18) !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    min-height: 46px;
    border-radius: 12px;
    background: linear-gradient(100deg, #5847dc, #386fe1);
    border: 1px solid rgba(145,125,255,0.55);
    color: white;
    font-weight: 700;
    transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease;
}


.stButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.10);
    box-shadow: 0 12px 35px rgba(70,75,225,0.42), 0 0 20px rgba(100,80,255,0.18);
}


.stButton > button:active {
    transform: translateY(1px) scale(0.98);
}


/* ============================================================
   CHAT
   ============================================================ */

[data-testid="stChatMessage"] {
    border-radius: 15px;
    transition: all 0.25s ease;
}


[data-testid="stChatMessage"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}


/* ============================================================
   CHAT INPUT
   ============================================================ */

[data-testid="stChatInput"] textarea {
    border-radius: 15px !important;
    background: rgba(6,9,27,0.94) !important;
    border: 1px solid rgba(105,105,175,0.38) !important;
    color: white !important;
    transition: all 0.3s ease !important;
}


[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(120,105,255,0.8) !important;
    box-shadow: 0 0 20px rgba(90,75,255,0.15) !important;
}


/* ============================================================
   INFO BOX
   ============================================================ */

[data-testid="stSidebar"] .stAlert {
    background: rgba(20,40,78,0.72) !important;
    border: 1px solid rgba(80,145,255,0.30) !important;
    border-radius: 14px !important;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 768px) {
    .login-container {
        width: 88vw;
        padding: 30px 24px;
        margin-top: 5vh;
    }

    .login-title {
        font-size: 26px;
    }

    .hero-box {
        width: 92%;
        padding: 32px 20px;
    }

    .hero-title {
        font-size: 28px;
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
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return (
            "⚠️ **Groq API key is missing.**\n\n"
            "Please set your `GROQ_API_KEY` environment variable."
        )

    client = Groq(api_key=api_key)

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
    st.markdown(
        """<div class="login-container">
    <div class="login-icon">⚛️</div>
    <div class="login-title">QUANTUM LAB</div>
    <div class="login-subtitle">AI-Powered Learning Space</div>
</div>""",
        unsafe_allow_html=True
    )

    st.subheader("🔐 Login")

    email = st.text_input(
        "Email address",
        placeholder="Enter your email"
    )

    if st.button("🚀 Login", use_container_width=True):
        if email.strip() == "":
            st.error("Please enter your email address.")
        else:
            st.session_state.user_email = email.strip()
            st.session_state.logged_in = True
            st.success("Login successful!")
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
        """<div class="quantum-brand">
    <div class="brand-icon">⚛</div>
    <div>
        <div class="brand-title">QUANTUM LAB</div>
        <div class="brand-subtitle">AI-Powered Learning Space</div>
    </div>
</div>""",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">👤 &nbsp; Logged In</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-email">{st.session_state.user_email}</div>', unsafe_allow_html=True)

    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    if st.button("✚  New Chat", use_container_width=True):
        chat_number = 1
        while f"New Quantum Chat {chat_number}" in st.session_state.chats:
            chat_number += 1

        new_chat_name = f"New Quantum Chat {chat_number}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
        st.toast("New chat created!")
        st.rerun()

    # --------------------------------------------------------
    # YOUR CHATS
    # --------------------------------------------------------
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 &nbsp; Your Chats</div>', unsafe_allow_html=True)

    chat_names = list(st.session_state.chats.keys())

    for chat_name in chat_names:
        is_current = chat_name == st.session_state.current_chat
        button_text = f"🟣 {chat_name}" if is_current else f"💬 {chat_name}"

        if st.button(button_text, key=f"open_{chat_name}", use_container_width=True):
            st.session_state.current_chat = chat_name
            st.rerun()

    # --------------------------------------------------------
    # RENAME CHAT
    # --------------------------------------------------------
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    with st.expander("✏️ Rename Current Chat"):
        current_name = st.session_state.current_chat
        new_name = st.text_input("New chat name", value=current_name, key="rename_input")

        if st.button("Save New Name", use_container_width=True):
            new_name = new_name.strip()

            if new_name == "":
                st.error("Chat name cannot be empty.")
            elif new_name == current_name:
                st.info("This is already the current name.")
            elif new_name in st.session_state.chats:
                st.error("A chat with this name already exists.")
            else:
                st.session_state.chats[new_name] = st.session_state.chats.pop(current_name)
                st.session_state.current_chat = new_name
                st.success("Chat renamed!")
                st.rerun()

    # --------------------------------------------------------
    # DELETE CURRENT CHAT
    # --------------------------------------------------------
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        current_name = st.session_state.current_chat

        if len(st.session_state.chats) == 1:
            st.session_state.chats[current_name] = []
            st.toast("Chat cleared!")
        else:
            del st.session_state.chats[current_name]
            remaining_chats = list(st.session_state.chats.keys())
            st.session_state.current_chat = remaining_chats[0]
            st.toast("Chat deleted!")

        st.rerun()

    # --------------------------------------------------------
    # CLEAR CONVERSATION
    # --------------------------------------------------------
    if st.button("🧹 Clear Conversation", use_container_width=True):
        current_name = st.session_state.current_chat
        st.session_state.chats[current_name] = []
        st.toast("Conversation cleared!")
        st.rerun()

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --------------------------------------------------------
    # LEARNING MODE
    # --------------------------------------------------------
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="learning-card">
    <div class="learning-header">
        <div class="learning-icon">🧠</div>
        <div>
            <div class="learning-title">LEARNING MODE</div>
            <div class="learning-status">QUANTUM KNOWLEDGE</div>
        </div>
    </div>
    <div class="learning-question">Ask questions about:</div>
    <div class="learning-topic"><span>⚛️</span> Quantum Computing</div>
    <div class="learning-topic"><span>🔵</span> Qubits</div>
    <div class="learning-topic"><span>〰️</span> Quantum Gates</div>
    <div class="learning-topic"><span>🧪</span> Qiskit</div>
</div>""",
        unsafe_allow_html=True
    )


# ============================================================
# MAIN AREA
# ============================================================

st.markdown(
    """<div class="hero-box">
    <div class="hero-icon">⚛️</div>
    <div class="hero-title">QUANTUM AI TUTOR</div>
    <div class="hero-subtitle">Explore quantum computing through conversation</div>
    <div class="online">● AI TUTOR ONLINE</div>
</div>""",
    unsafe_allow_html=True
)


# ============================================================
# CHAT INTERFACE
# ============================================================

current_chat = st.session_state.current_chat
messages = st.session_state.chats[current_chat]

# Display existing chat messages
for message in messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
if prompt := st.chat_input("Ask anything about quantum computing..."):pythi
    # Append user prompt
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate and append AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = answer_question(prompt, messages)
            st.write(response_text)

    messages.append({"role": "assistant", "content": response_text})
