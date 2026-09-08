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
# GALAXY THEME
# ============================================================

st.markdown(
    """
<style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    html, body, [class*="css"] {
        font-family: "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(100, 60, 255, 0.18),
                transparent 25%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(0, 180, 255, 0.13),
                transparent 25%
            ),
            radial-gradient(
                circle at 50% 90%,
                rgba(150, 50, 255, 0.12),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #02030d 0%,
                #080a24 45%,
                #020817 100%
            );

        color: white;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    [data-testid="stMain"] {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }


    /* ======================================================
       STAR EFFECT
       ====================================================== */

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;

        background-image:
            radial-gradient(
                1px 1px at 10% 20%,
                rgba(255,255,255,0.7),
                transparent
            ),
            radial-gradient(
                1px 1px at 30% 70%,
                rgba(160,180,255,0.7),
                transparent
            ),
            radial-gradient(
                1px 1px at 70% 30%,
                rgba(255,255,255,0.6),
                transparent
            ),
            radial-gradient(
                1px 1px at 90% 75%,
                rgba(120,200,255,0.7),
                transparent
            ),
            linear-gradient(
                rgba(100,100,255,0.025) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(100,100,255,0.025) 1px,
                transparent 1px
            );

        background-size:
            auto,
            auto,
            auto,
            auto,
            45px 45px,
            45px 45px;

        pointer-events: none;
        z-index: 0;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        background:
            radial-gradient(
                circle at 20% 10%,
                rgba(100, 60, 255, 0.20),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 80%,
                rgba(0, 180, 255, 0.10),
                transparent 30%
            ),
            linear-gradient(
                180deg,
                #050618,
                #07091d,
                #030411
            );

        border-right: 1px solid rgba(115, 100, 255, 0.25);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }


    /* ======================================================
       SIDEBAR BRAND
       ====================================================== */

    .brand-container {
        padding: 8px 0 18px 0;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
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
                #7548ff,
                #287cf0
            );

        border: 1px solid rgba(180,160,255,0.5);

        box-shadow:
            0 0 20px rgba(105,70,255,0.55),
            inset 0 0 15px rgba(255,255,255,0.12);

        font-size: 22px;
    }

    .brand-title {
        color: white;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 1px;
    }

    .brand-subtitle {
        color: #7d84a8;
        font-size: 11px;
        margin-top: 4px;
    }


    /* ======================================================
       SIDEBAR DIVIDERS
       ====================================================== */

    [data-testid="stSidebar"] hr {
        border: none;
        border-top: 1px solid rgba(130,120,255,0.16);
        margin: 16px 0;
    }


    /* ======================================================
       USER CARD
       ====================================================== */

    .user-card {
        padding: 13px;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(35,35,70,0.65),
                rgba(10,12,30,0.75)
            );

        border: 1px solid rgba(120,110,255,0.16);
    }

    .user-label {
        color: #d5d8ea;
        font-size: 14px;
        font-weight: 700;
    }

    .user-email {
        color: #5b9dff;
        font-size: 12px;
        margin-top: 5px;
        word-break: break-word;
    }


    /* ======================================================
       SIDEBAR BUTTONS
       ====================================================== */

    [data-testid="stSidebar"] .stButton > button {

        min-height: 44px;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(29,32,66,0.95),
                rgba(18,21,48,0.95)
            );

        border: 1px solid rgba(115,105,255,0.24);

        color: #c9cce0;

        font-weight: 600;

        transition:
            transform 0.2s ease,
            background 0.25s ease,
            border-color 0.25s ease,
            box-shadow 0.25s ease;

        box-shadow:
            0 4px 15px rgba(0,0,0,0.18);
    }

    [data-testid="stSidebar"] .stButton > button:hover {

        transform: translateY(-2px);

        background:
            linear-gradient(
                135deg,
                rgba(92,65,220,0.9),
                rgba(38,105,210,0.85)
            );

        border-color: rgba(145,130,255,0.8);

        color: white;

        box-shadow:
            0 8px 25px rgba(76,65,255,0.3);
    }

    [data-testid="stSidebar"] .stButton > button:active {
        transform: scale(0.97);
    }


    /* ======================================================
       LEARNING MODE
       ====================================================== */

    .learning-card {

        margin-top: 8px;

        padding: 18px;

        border-radius: 16px;

        background:
            radial-gradient(
                circle at 90% 10%,
                rgba(70,130,255,0.18),
                transparent 35%
            ),
            linear-gradient(
                145deg,
                #12325f,
                #0a1d3e
            );

        border: 1px solid rgba(75,145,255,0.45);

        box-shadow:
            0 0 25px rgba(30,100,255,0.12),
            inset 0 0 25px rgba(100,100,255,0.04);
    }

    .learning-header {

        display: flex;

        align-items: center;

        gap: 12px;

        margin-bottom: 17px;
    }

    .learning-icon {

        width: 42px;
        height: 42px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(255,90,225,0.25),
                rgba(100,70,255,0.35)
            );

        border: 1px solid rgba(210,130,255,0.35);

        font-size: 21px;

        box-shadow:
            0 0 18px rgba(150,80,255,0.25);
    }

    .learning-title {

        color: #ffffff;

        font-size: 14px;

        font-weight: 800;

        letter-spacing: 0.6px;
    }

    .learning-status {

        color: #73a9ff;

        font-size: 10px;

        margin-top: 3px;

        letter-spacing: 1px;
    }

    .learning-question {

        color: #b7c3df;

        font-size: 13px;

        margin-bottom: 10px;
    }

    .learning-topic {

        display: flex;

        align-items: center;

        gap: 10px;

        padding: 8px 9px;

        margin: 3px 0;

        border-radius: 9px;

        color: #d2d8ec;

        font-size: 13px;

        transition:
            background 0.2s ease,
            transform 0.2s ease,
            color 0.2s ease;
    }

    .learning-topic:hover {

        background: rgba(100,125,255,0.13);

        transform: translateX(5px);

        color: white;
    }

    .learning-topic span:first-child {
        width: 24px;
        text-align: center;
    }

    .quantum-dots {

        display: flex;

        gap: 6px;

        margin-top: 14px;
    }

    .quantum-dots span {

        width: 5px;
        height: 5px;

        border-radius: 50%;

        background: #8c7cff;

        box-shadow:
            0 0 8px rgba(125,110,255,0.9);
    }


    /* ======================================================
       MAIN HERO
       ====================================================== */

    .hero-box {

        position: relative;

        overflow: hidden;

        margin: 25px auto 28px auto;

        padding: 45px 20px;

        max-width: 1050px;

        text-align: center;

        border-radius: 22px;

        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(120,70,255,0.18),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 30%,
                rgba(0,190,255,0.12),
                transparent 30%
            ),
            linear-gradient(
                145deg,
                rgba(20,23,57,0.96),
                rgba(7,10,30,0.98)
            );

        border: 1px solid rgba(120,105,255,0.38);

        box-shadow:
            0 0 55px rgba(70,55,255,0.11),
            inset 0 0 40px rgba(80,60,255,0.04);
    }

    .hero-box::before {

        content: "✦";

        position: absolute;

        top: 18px;
        left: 28px;

        color: rgba(255,255,255,0.5);

        font-size: 12px;
    }

    .hero-box::after {

        content: "✧";

        position: absolute;

        bottom: 20px;
        right: 32px;

        color: rgba(100,190,255,0.5);

        font-size: 16px;
    }

    .hero-icon {

        width: 76px;
        height: 76px;

        margin: auto;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 50%;

        background:
            radial-gradient(
                circle,
                rgba(125,90,255,0.32),
                rgba(40,60,160,0.12)
            );

        border: 1px solid rgba(140,120,255,0.45);

        box-shadow:
            0 0 30px rgba(115,80,255,0.35);

        font-size: 48px;
    }

    .hero-title {

        color: #ffffff;

        font-size: 38px;

        font-weight: 850;

        letter-spacing: 1px;

        margin-top: 17px;

        text-shadow:
            0 0 20px rgba(125,95,255,0.35);
    }

    .hero-subtitle {

        color: #9da6c9;

        font-size: 15px;

        margin-top: 8px;
    }

    .online {

        color: #42e99a;

        font-size: 12px;

        margin-top: 16px;

        letter-spacing: 1.3px;

        text-shadow:
            0 0 10px rgba(65,235,150,0.35);
    }


    /* ======================================================
       LOGIN
       ====================================================== */

    .login-wrapper {

        max-width: 620px;

        margin: 60px auto 20px auto;
    }

    .login-box {

        padding: 45px;

        text-align: center;

        border-radius: 22px;

        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(115,70,255,0.20),
                transparent 40%
            ),
            linear-gradient(
                145deg,
                rgba(20,23,57,0.97),
                rgba(7,10,30,0.99)
            );

        border: 1px solid rgba(120,105,255,0.4);

        box-shadow:
            0 0 60px rgba(75,55,255,0.13),
            inset 0 0 40px rgba(80,60,255,0.04);
    }

    .login-title {

        margin-top: 16px;

        color: white;

        font-size: 32px;

        font-weight: 850;

        letter-spacing: 1px;
    }

    .login-subtitle {

        color: #9299bb;

        font-size: 14px;

        margin-top: 7px;
    }


    /* ======================================================
       INPUT
       ====================================================== */

    .stTextInput input {

        min-height: 45px;

        border-radius: 12px;

        background:
            rgba(5,8,25,0.90);

        border: 1px solid rgba(115,105,255,0.25);

        color: white;

        transition:
            border-color 0.25s ease,
            box-shadow 0.25s ease;
    }

    .stTextInput input:focus {

        border-color: #7c6cff;

        box-shadow:
            0 0 18px rgba(100,80,255,0.25);
    }


    /* ======================================================
       ALL MAIN BUTTONS
       ====================================================== */

    .stButton > button {

        min-height: 45px;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                #6548ff,
                #287be8
            );

        border: 1px solid rgba(150,135,255,0.55);

        color: white;

        font-weight: 700;

        transition:
            transform 0.2s ease,
            box-shadow 0.25s ease,
            filter 0.25s ease;
    }

    .stButton > button:hover {

        transform: translateY(-2px);

        filter: brightness(1.08);

        box-shadow:
            0 10px 30px rgba(70,65,255,0.30);
    }

    .stButton > button:active {
        transform: scale(0.97);
    }


    /* ======================================================
       CHAT
       ====================================================== */

    [data-testid="stChatMessage"] {

        border-radius: 15px;

        background:
            rgba(7,10,28,0.38);

        border: 1px solid rgba(115,105,255,0.08);
    }

    [data-testid="stChatMessageContent"] {

        color: #e4e7f5;

        line-height: 1.65;
    }


    /* ======================================================
       CHAT INPUT
       ====================================================== */

    [data-testid="stChatInput"] textarea {

        background:
            rgba(8,12,32,0.95);

        border: 1px solid rgba(110,100,255,0.30);

        color: white;

        border-radius: 14px;

        transition:
            border-color 0.25s ease,
            box-shadow 0.25s ease;
    }

    [data-testid="stChatInput"] textarea:focus {

        border-color: #796cff;

        box-shadow:
            0 0 20px rgba(95,75,255,0.25);
    }


    /* ======================================================
       EXPANDER
       ====================================================== */

    [data-testid="stSidebar"] details {

        border-color: rgba(120,110,255,0.25);
        border-radius: 12px;
        background: rgba(10,12,30,0.45);
    }


    /* ======================================================
       SCROLLBAR
       ====================================================== */

    ::-webkit-scrollbar {
        width: 7px;
    }

    ::-webkit-scrollbar-track {
        background: #02030d;
    }

    ::-webkit-scrollbar-thumb {

        background:
            linear-gradient(
                180deg,
                #674fff,
                #287be8
            );

        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #8a7cff;
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

    client = Groq(
        api_key=api_key
    )

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
        """
<div class="login-wrapper">

    <div class="login-box">

        <div class="hero-icon">
            ⚛️
        </div>

        <div class="login-title">
            QUANTUM LAB
        </div>

        <div class="login-subtitle">
            AI-Powered Learning Space
        </div>

    </div>

</div>
""",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("🔐 Login")

    email = st.text_input(
        "Email address",
        placeholder="Enter your email"
    )

    if st.button(
        "🚀 Login",
        use_container_width=True
    ):

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

    # ========================================================
    # BRAND
    # ========================================================

    st.markdown(
        """
<div class="brand-container">

    <div class="brand-row">

        <div class="brand-icon">
            ⚛️
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

</div>
""",
        unsafe_allow_html=True
    )


    st.markdown("---")


    # ========================================================
    # USER
    # ========================================================

    st.markdown(
        f"""
<div class="user-card">

    <div class="user-label">
        👤 Logged In
    </div>

    <div class="user-email">
        {st.session_state.user_email}
    </div>

</div>
""",
        unsafe_allow_html=True
    )


    st.markdown("---")


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "➕  New Chat",
        use_container_width=True
    ):

        chat_number = 1

        while f"New Quantum Chat {chat_number}" in st.session_state.chats:
            chat_number += 1

        new_chat_name = f"New Quantum Chat {chat_number}"

        st.session_state.chats[new_chat_name] = []

        st.session_state.current_chat = new_chat_name

        st.toast("New chat created!")

        st.rerun()


    st.markdown("---")


    # ========================================================
    # YOUR CHATS
    # ========================================================

    st.subheader("💬 Your Chats")

    chat_names = list(
        st.session_state.chats.keys()
    )

    for chat_name in chat_names:

        is_current = (
            chat_name == st.session_state.current_chat
        )

        if is_current:
            button_text = f"🟣  {chat_name}"
        else:
            button_text = f"💬  {chat_name}"

        if st.button(
            button_text,
            key=f"open_{chat_name}",
            use_container_width=True
        ):

            st.session_state.current_chat = chat_name

            st.rerun()


    st.markdown("---")


    # ========================================================
    # RENAME CHAT
    # ========================================================

    with st.expander("✏️ Rename Current Chat"):

        current_name = st.session_state.current_chat

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
                st.error("Chat name cannot be empty.")

            elif new_name == current_name:
                st.info("This is already the current name.")

            elif new_name in st.session_state.chats:
                st.error("A chat with this name already exists.")

            else:

                st.session_state.chats[new_name] = (
                    st.session_state.chats.pop(current_name)
                )

                st.session_state.current_chat = new_name

                st.success("Chat renamed!")

                st.rerun()


    st.markdown("---")


    # ========================================================
    # DELETE CURRENT CHAT
    # ========================================================

    if st.button(
        "🗑️  Delete Current Chat",
        use_container_width=True
    ):

        current_name = st.session_state.current_chat

        if len(st.session_state.chats) == 1:

            st.session_state.chats[current_name] = []

            st.toast("Chat cleared!")

        else:

            del st.session_state.chats[current_name]

            remaining_chats = list(
                st.session_state.chats.keys()
            )

            st.session_state.current_chat = remaining_chats[0]

            st.toast("Chat deleted!")

        st.rerun()


    # ========================================================
    # CLEAR CONVERSATION
    # ========================================================

    if st.button(
        "🧹  Clear Conversation",
        use_container_width=True
    ):

        current_name = st.session_state.current_chat

        st.session_state.chats[current_name] = []

        st.toast("Conversation cleared!")

        st.rerun()


    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button(
        "🚪  Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.rerun()


    # ========================================================
    # LEARNING MODE
    # ========================================================

    st.markdown("---")

    st.markdown(
        """
<div class="learning-card">

    <div class="learning-header">

        <div class="learning-icon">
            🧠
        </div>

        <div>

            <div class="learning-title">
                LEARNING MODE
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
        <span>Quantum Computing</span>
    </div>


    <div class="learning-topic">
        <span>🔵</span>
        <span>Qubits</span>
    </div>


    <div class="learning-topic">
        <span>〰️</span>
        <span>Quantum Gates</span>
    </div>


    <div class="learning-topic">
        <span>🧪</span>
        <span>Qiskit</span>
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


# ============================================================
# CURRENT CHAT
# ============================================================

current_chat = st.session_state.current_chat

messages = st.session_state.chats[current_chat]


# ============================================================
# DISPLAY CHAT
# ============================================================

for message in messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.markdown(message["content"])

    else:

        with st.chat_message("assistant"):
            st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask anything about quantum computing..."
)


# ============================================================
# CHAT LOGIC
# ============================================================

if question:

    # User message
    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(question)

    # AI response
    with st.chat_message("assistant"):

        with st.spinner("🌌 Exploring the quantum universe..."):

            answer = answer_question(
                question,
                messages
            )

            st.markdown(answer)

    # Save AI response
    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # Save conversation
    st.session_state.chats[current_chat] = messages

    st.rerun()
