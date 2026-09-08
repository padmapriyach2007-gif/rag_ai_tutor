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
# GALAXY THEME CSS
# ============================================================

st.markdown(
    """
<style>

    /* ========================================================
       GLOBAL GALAXY BACKGROUND
       ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 15% 20%,
                rgba(93, 53, 255, 0.18),
                transparent 28%
            ),
            radial-gradient(
                circle at 85% 15%,
                rgba(0, 183, 255, 0.16),
                transparent 28%
            ),
            radial-gradient(
                circle at 50% 85%,
                rgba(160, 45, 255, 0.14),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #030412 0%,
                #080b24 45%,
                #020817 100%
            );

        color: #ffffff;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(111, 66, 255, 0.12),
                transparent 25%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(0, 212, 255, 0.10),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #030412,
                #080b24,
                #020817
            );
    }

    [data-testid="stMain"] {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* ========================================================
       GALAXY GRID
       ======================================================== */

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;

        background-image:
            linear-gradient(
                rgba(120, 110, 255, 0.035) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(120, 110, 255, 0.035) 1px,
                transparent 1px
            );

        background-size: 45px 45px;

        pointer-events: none;
        z-index: 0;
    }

    /* ========================================================
       STAR FIELD
       ======================================================== */

    [data-testid="stAppViewContainer"]::after {
        content: "✦     ·        ✧          ·     ✦             ·      ✧       ·        ✦        ·      ✧";

        position: fixed;
        inset: 0;

        color: rgba(255,255,255,0.22);
        font-size: 13px;
        line-height: 65px;
        letter-spacing: 18px;

        pointer-events: none;
        z-index: 0;

        overflow: hidden;
        white-space: normal;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background:
            radial-gradient(
                circle at 20% 10%,
                rgba(93, 53, 255, 0.20),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(0, 179, 255, 0.10),
                transparent 30%
            ),
            linear-gradient(
                180deg,
                #050619 0%,
                #07091b 50%,
                #030514 100%
            );

        border-right: 1px solid rgba(119, 103, 255, 0.25);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] h1 {
        color: #ffffff;
        letter-spacing: 1px;
        font-weight: 800;
    }

    [data-testid="stSidebar"] p {
        color: #9298b8;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(125, 115, 255, 0.18);
    }


    /* ========================================================
       SIDEBAR BRAND
       ======================================================== */

    .brand-container {
        padding: 10px 2px 18px 2px;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-icon {
        width: 42px;
        height: 42px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                #704cff,
                #3b8dff
            );

        box-shadow:
            0 0 18px rgba(112, 76, 255, 0.55),
            inset 0 0 12px rgba(255,255,255,0.12);

        font-size: 22px;
    }

    .brand-title {
        color: #ffffff;
        font-size: 21px;
        font-weight: 800;
        letter-spacing: 0.8px;
    }

    .brand-subtitle {
        color: #747b9f;
        font-size: 12px;
        margin-top: 5px;
        letter-spacing: 0.4px;
    }


    /* ========================================================
       USER INFO
       ======================================================== */

    .user-card {
        padding: 13px 14px;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(255,255,255,0.045),
                rgba(255,255,255,0.018)
            );

        border: 1px solid rgba(130,120,255,0.16);

        box-shadow:
            inset 0 0 20px rgba(110,80,255,0.025);
    }

    .user-label {
        color: #c9cce0;
        font-size: 14px;
        font-weight: 700;
    }

    .user-email {
        color: #4e9dff;
        font-size: 12px;
        margin-top: 5px;
        word-break: break-all;
    }


    /* ========================================================
       SIDEBAR BUTTONS
       ======================================================== */

    [data-testid="stSidebar"] .stButton > button {

        width: 100%;
        min-height: 44px;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                rgba(36, 38, 72, 0.90),
                rgba(22, 25, 53, 0.95)
            );

        border: 1px solid rgba(118, 108, 255, 0.22);

        color: #c5c8dd;

        font-weight: 600;

        transition:
            all 0.25s ease,
            transform 0.2s ease;

        box-shadow:
            0 4px 14px rgba(0,0,0,0.18);
    }

    [data-testid="stSidebar"] .stButton > button:hover {

        background:
            linear-gradient(
                135deg,
                rgba(101, 72, 255, 0.65),
                rgba(36, 112, 255, 0.55)
            );

        border-color: #796cff;

        color: white;

        transform: translateY(-2px);

        box-shadow:
            0 8px 24px rgba(82, 66, 255, 0.28);
    }

    [data-testid="stSidebar"] .stButton > button:active {
        transform: scale(0.98);
    }


    /* ========================================================
       LEARNING MODE
       ======================================================== */

    .learning-card {

        margin-top: 10px;

        padding: 20px 18px;

        border-radius: 16px;

        background:
            radial-gradient(
                circle at 85% 15%,
                rgba(75, 129, 255, 0.20),
                transparent 35%
            ),
            linear-gradient(
                145deg,
                rgba(19, 51, 96, 0.95),
                rgba(10, 27, 58, 0.98)
            );

        border: 1px solid rgba(82, 142, 255, 0.38);

        box-shadow:
            0 0 25px rgba(40, 100, 255, 0.12),
            inset 0 0 25px rgba(0, 170, 255, 0.035);
    }

    .learning-header {

        display: flex;
        align-items: center;

        gap: 12px;

        margin-bottom: 18px;
    }

    .learning-icon {

        width: 40px;
        height: 40px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 11px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 100, 230, 0.22),
                rgba(111, 81, 255, 0.30)
            );

        border: 1px solid rgba(196, 126, 255, 0.30);

        font-size: 21px;

        box-shadow:
            0 0 15px rgba(159, 91, 255, 0.20);
    }

    .learning-title {

        color: #ffffff;

        font-size: 14px;

        font-weight: 800;

        letter-spacing: 0.5px;
    }

    .learning-status {

        color: #79aaff;

        font-size: 10px;

        margin-top: 3px;

        letter-spacing: 1px;
    }

    .learning-question {

        color: #b9c3df;

        font-size: 13px;

        margin-bottom: 12px;
    }

    .learning-topic {

        display: flex;

        align-items: center;

        gap: 10px;

        padding: 8px 10px;

        margin: 4px 0;

        border-radius: 9px;

        color: #d2d8ec;

        font-size: 13px;

        transition: all 0.2s ease;
    }

    .learning-topic:hover {

        background: rgba(105, 124, 255, 0.12);

        transform: translateX(4px);

        color: white;
    }

    .learning-topic span {

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

        background: #7785ff;

        box-shadow:
            0 0 8px rgba(120,130,255,0.8);
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero-box {

        position: relative;

        overflow: hidden;

        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(113, 69, 255, 0.16),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 30%,
                rgba(0, 198, 255, 0.12),
                transparent 30%
            ),
            linear-gradient(
                145deg,
                rgba(19, 22, 53, 0.96),
                rgba(8, 12, 33, 0.98)
            );

        border: 1px solid rgba(112, 101, 255, 0.35);

        border-radius: 22px;

        padding: 48px 20px;

        text-align: center;

        margin-top: 22px;
        margin-bottom: 28px;

        box-shadow:
            0 0 45px rgba(73, 56, 255, 0.10),
            inset 0 0 40px rgba(83, 63, 255, 0.035);
    }

    .hero-box::before {

        content: "✦";

        position: absolute;

        top: 18px;
        left: 25px;

        color: rgba(255,255,255,0.40);

        font-size: 12px;
    }

    .hero-box::after {

        content: "✧";

        position: absolute;

        bottom: 18px;
        right: 30px;

        color: rgba(120,180,255,0.45);

        font-size: 16px;
    }

    .hero-icon {

        font-size: 54px;

        display: inline-flex;

        align-items: center;
        justify-content: center;

        width: 78px;
        height: 78px;

        border-radius: 50%;

        background:
            radial-gradient(
                circle,
                rgba(132, 93, 255, 0.30),
                rgba(32, 68, 160, 0.12)
            );

        border: 1px solid rgba(136, 116, 255, 0.40);

        box-shadow:
            0 0 30px rgba(113, 81, 255, 0.35);
    }

    .hero-title {

        font-size: 38px;

        font-weight: 850;

        color: #ffffff;

        margin-top: 18px;

        letter-spacing: 1px;

        text-shadow:
            0 0 18px rgba(126, 98, 255, 0.35);
    }

    .hero-subtitle {

        font-size: 15px;

        color: #9ca5c8;

        margin-top: 8px;
    }

    .online {

        color: #43e89a;

        font-size: 12px;

        margin-top: 16px;

        letter-spacing: 1.2px;

        text-shadow:
            0 0 10px rgba(67, 232, 154, 0.35);
    }


    /* ========================================================
       CHAT AREA
       ======================================================== */

    [data-testid="stChatMessage"] {

        border-radius: 16px;

        border: 1px solid rgba(112, 101, 255, 0.10);

        background: rgba(8, 12, 31, 0.35);
    }

    [data-testid="stChatMessageContent"] {

        color: #e4e7f4;

        line-height: 1.65;
    }


    /* ========================================================
       CHAT INPUT
       ======================================================== */

    [data-testid="stChatInput"] {

        border-radius: 16px;
    }

    [data-testid="stChatInput"] textarea {

        background:
            rgba(12, 16, 40, 0.95);

        border: 1px solid rgba(110, 101, 255, 0.30);

        color: white;

        border-radius: 14px;

        transition: all 0.25s ease;
    }

    [data-testid="stChatInput"] textarea:focus {

        border-color: #776aff;

        box-shadow:
            0 0 18px rgba(101, 81, 255, 0.25);
    }


    /* ========================================================
       LOGIN BOX
       ======================================================== */

    .login-wrapper {

        max-width: 620px;

        margin: 55px auto 0 auto;
    }

    .login-box {

        position: relative;

        overflow: hidden;

        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(113, 74, 255, 0.18),
                transparent 40%
            ),
            linear-gradient(
                145deg,
                rgba(18, 21, 52, 0.98),
                rgba(6, 9, 28, 0.98)
            );

        border: 1px solid rgba(116, 101, 255, 0.38);

        border-radius: 22px;

        padding: 48px 45px;

        text-align: center;

        box-shadow:
            0 0 60px rgba(78, 58, 255, 0.12),
            inset 0 0 35px rgba(87, 68, 255, 0.035);
    }

    .login-title {

        color: white;

        font-size: 32px;

        font-weight: 800;

        margin-top: 15px;
    }

    .login-subtitle {

        color: #9299bb;

        font-size: 14px;

        margin-top: 7px;
    }


    /* ========================================================
       LOGIN INPUT
       ======================================================== */

    .stTextInput input {

        background: rgba(7, 11, 30, 0.85);

        color: white;

        border: 1px solid rgba(112, 101, 255, 0.25);

        border-radius: 12px;

        min-height: 45px;

        transition: all 0.25s ease;
    }

    .stTextInput input:focus {

        border-color: #786aff;

        box-shadow:
            0 0 18px rgba(98, 77, 255, 0.20);
    }


    /* ========================================================
       LOGIN BUTTON
       ======================================================== */

    .stButton > button {

        border-radius: 12px;

        min-height: 46px;

        background:
            linear-gradient(
                135deg,
                #6548ff,
                #2879e8
            );

        border: 1px solid rgba(140, 125, 255, 0.60);

        color: white;

        font-weight: 700;

        transition:
            all 0.25s ease,
            transform 0.2s ease;

        box-shadow:
            0 8px 25px rgba(69, 67, 255, 0.20);
    }

    .stButton > button:hover {

        transform: translateY(-2px);

        box-shadow:
            0 12px 32px rgba(69, 67, 255, 0.35);

        border-color: #9b8eff;
    }

    .stButton > button:active {

        transform: scale(0.98);
    }


    /* ========================================================
       INFO BOX
       ======================================================== */

    [data-testid="stAlert"] {

        border-radius: 13px;
    }


    /* ========================================================
       SCROLLBAR
       ======================================================== */

    ::-webkit-scrollbar {
        width: 7px;
    }

    ::-webkit-scrollbar-track {
        background: #030514;
    }

    ::-webkit-scrollbar-thumb {

        background:
            linear-gradient(
                180deg,
                #5c4cff,
                #2879e8
            );

        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #796cff;
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

    chat_names = list(st.session_state.chats.keys())

    for chat_name in chat_names:

        is_current = (
            chat_name == st.session_state.current_chat
        )

        button_text = (
            f"🟣  {chat_name}"
            if is_current
            else f"💬  {chat_name}"
        )

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
# MAIN HERO
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
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):
        st.markdown(question)


    # --------------------------------------------------------
    # GENERATE RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("🌌 Exploring the quantum universe..."):

            answer = answer_question(
                question,
                messages
            )

            st.markdown(answer)


    # --------------------------------------------------------
    # SAVE AI RESPONSE
    # --------------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # --------------------------------------------------------
    # SAVE CHAT STATE
    # --------------------------------------------------------

    st.session_state.chats[current_chat] = messages

    st.rerun()
