import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Quantum Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "chats" not in st.session_state:
    st.session_state.chats = {
        "Quantum Learning": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Quantum Learning"


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

    /* ================= MAIN BACKGROUND ================= */

    .stApp {
        background: #07091a;
    }

    [data-testid="stMain"] {
        background: #07091a;
    }

    /* ================= SIDEBAR ================= */

    [data-testid="stSidebar"] {
        background: #08091b;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 25px;
    }

    .brand-title {
        font-size: 25px;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }

    .brand-subtitle {
        font-size: 14px;
        color: #a7aac4;
    }

    .user-box {
        margin-top: 28px;
        margin-bottom: 20px;
        color: white;
        font-size: 15px;
    }

    .email {
        color: #8c90a8;
        font-size: 13px;
        margin-top: 5px;
    }

    .sidebar-heading {
        color: white;
        font-size: 17px;
        font-weight: 600;
        margin-top: 22px;
        margin-bottom: 10px;
    }

    .chat-active {
        background: #17192b;
        border-radius: 8px;
        padding: 10px;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .divider {
        height: 1px;
        background: #292b3d;
        margin: 20px 0;
    }

    /* ================= BUTTONS ================= */

    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        min-height: 42px;
        border-radius: 8px;
        border: 1px solid #3c3e50;
        background: #292b37;
        color: white;
        font-size: 14px;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        border-color: #4da3ff;
        background: #353746;
        color: white;
    }

    /* ================= LEARNING BOX ================= */

    .learning-box {
        background: #10294e;
        border: 1px solid #193d70;
        border-radius: 10px;
        padding: 17px;
        margin-top: 20px;
    }

    .learning-title {
        color: #4da3ff;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .learning-text {
        color: #c0c8dd;
        font-size: 14px;
        line-height: 1.8;
    }

    /* ================= HERO ================= */

    .hero {
        background: #191b25;
        border: 1px solid #292c3a;
        border-radius: 15px;
        text-align: center;
        padding: 55px 25px;
        margin-top: 45px;
        margin-bottom: 25px;
    }

    .quantum-symbol {
        font-size: 45px;
        margin-bottom: 10px;
    }

    .hero-title {
        color: white;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        color: #aeb1c5;
        font-size: 17px;
        margin-bottom: 18px;
    }

    .online {
        color: #42e88b;
    }

    .status-text {
        color: #b9bbc9;
        font-size: 14px;
    }

    /* ================= CHAT ================= */

    .chat-user {
        background: #252735;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0;
        color: white;
    }

    .chat-ai {
        background: #11131d;
        border: 1px solid #292c3a;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #e6e7ef;
    }

    .chat-label {
        font-size: 12px;
        color: #8e93aa;
        margin-bottom: 5px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# AI RESPONSE
# =========================================================

def quantum_response(question):

    q = question.lower().strip()

    if "qubit" in q:
        return """
**A qubit** is the basic unit of quantum information.

A classical bit can be either **0 or 1**.

A qubit can exist in a combination of both states:

**|ψ⟩ = α|0⟩ + β|1⟩**

This is called **superposition**.
"""

    elif "superposition" in q:
        return """
**Superposition** means that a quantum system can exist in a
combination of multiple possible states.

For a qubit:

**|ψ⟩ = α|0⟩ + β|1⟩**

When we measure it, we obtain either 0 or 1.
"""

    elif "entanglement" in q:
        return """
**Quantum entanglement** is a phenomenon where two or more
qubits become strongly correlated.

The state of one qubit is connected to the state of another,
even when they are separated.
"""

    elif "hadamard" in q:
        return """
The **Hadamard (H) gate** is used to create superposition.

For example:

**H|0⟩ = (|0⟩ + |1⟩) / √2**

It is one of the most important quantum gates.
"""

    elif "cnot" in q:
        return """
**CNOT** stands for Controlled-NOT.

It uses:

• One control qubit
• One target qubit

The target qubit is flipped when the control qubit is **1**.
"""

    elif "qiskit" in q:
        return """
**Qiskit** is a Python-based framework for working with quantum
computing.

You can use it to:

• Create quantum circuits
• Apply quantum gates
• Simulate circuits
• Run quantum programs
"""

    elif "gate" in q:
        return """
Common **quantum gates** include:

• X gate — quantum NOT
• Y gate
• Z gate
• H gate — creates superposition
• S gate
• T gate
• CNOT — controlled operation
"""

    elif q in ["hi", "hello", "hey"]:
        return """
Hello! 👋

I'm your **Quantum AI Tutor**.

You can ask me about:

• Qubits
• Superposition
• Entanglement
• Quantum gates
• Quantum circuits
• Qiskit
"""

    else:
        return f"""
You asked:

**{question}**

I can help you learn quantum computing.

Try asking:

**What is a qubit?**

or

**What is superposition?**
"""


# =========================================================
# LOGIN SCREEN
# =========================================================

if not st.session_state.logged_in:

    st.markdown("""
    <div class="hero">

        <div class="quantum-symbol">⚛️</div>

        <div class="hero-title">
            Quantum Lab
        </div>

        <div class="hero-subtitle">
            AI-Powered Learning Space
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.info("You are logged out.")

    if st.button("🔐 Login", use_container_width=True):
        st.session_state.logged_in = True
        st.toast("Logged in successfully!")
        st.rerun()

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # Brand
    st.markdown("""
    <div class="brand-title">
        ⚛️ QUANTUM LAB
    </div>

    <div class="brand-subtitle">
        AI-Powered Learning Space
    </div>
    """, unsafe_allow_html=True)


    # User
    st.markdown("""
    <div class="user-box">
        👤 <b>Logged In</b>
        <div class="email">
            your@email.com
        </div>
    </div>
    """, unsafe_allow_html=True)


    # NEW CHAT
    if st.button("➕  New Chat", use_container_width=True):

        number = len(st.session_state.chats) + 1

        new_name = f"New Quantum Chat {number}"

        st.session_state.chats[new_name] = []

        st.session_state.current_chat = new_name

        st.toast("New chat created!")

        st.rerun()


    # CHAT LIST
    st.markdown(
        '<div class="sidebar-heading">💬 Your Chats</div>',
        unsafe_allow_html=True
    )


    for chat_name in st.session_state.chats:

        if st.button(
            f"💬 {chat_name}",
            key=f"chat_{chat_name}",
            use_container_width=True
        ):

            st.session_state.current_chat = chat_name

            st.rerun()


    st.markdown('<div class="divider"></div>',
                unsafe_allow_html=True)


    # DELETE CURRENT CHAT
    if st.button(
        "🗑️  Delete Current Chat",
        use_container_width=True
    ):

        current = st.session_state.current_chat

        if len(st.session_state.chats) > 1:

            del st.session_state.chats[current]

            st.session_state.current_chat = list(
                st.session_state.chats.keys()
            )[0]

            st.toast("Chat deleted!")

        else:

            st.session_state.chats[current] = []

            st.toast("Current chat cleared!")


        st.rerun()


    # CLEAR CONVERSATION
    if st.button(
        "🧹  Clear Conversation",
        use_container_width=True
    ):

        current = st.session_state.current_chat

        st.session_state.chats[current] = []

        st.toast("Conversation cleared!")

        st.rerun()


    # LOGOUT
    if st.button(
        "🚪  Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.toast("Logged out!")

        st.rerun()


    st.markdown('<div class="divider"></div>',
                unsafe_allow_html=True)


    # LEARNING MODE
    st.markdown("""
    <div class="learning-box">

        <div class="learning-title">
            🧠 Learning Mode
        </div>

        <div class="learning-text">
            Ask questions about:<br><br>
            • Quantum Computing<br>
            • Qubits<br>
            • Quantum Gates<br>
            • Qiskit
        </div>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN CONTENT
# =========================================================

st.markdown("""
<div class="hero">

    <div class="quantum-symbol">
        ⚛️
    </div>

    <div class="hero-title">
        Quantum AI Tutor
    </div>

    <div class="hero-subtitle">
        Explore quantum computing through conversation
    </div>

    <div class="status-text">
        <span class="online">●</span>
        &nbsp; AI TUTOR ONLINE
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# CURRENT CHAT
# =========================================================

current_chat = st.session_state.current_chat

messages = st.session_state.chats[current_chat]


# =========================================================
# DISPLAY MESSAGES
# =========================================================

for message in messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.markdown(message["content"])

    else:

        with st.chat_message("assistant"):
            st.markdown(message["content"])


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask anything about quantum computing..."
)


if question:

    # Add user message
    messages.append({
        "role": "user",
        "content": question
    })

    # Generate answer
    answer = quantum_response(question)

    # Add AI message
    messages.append({
        "role": "assistant",
        "content": answer
    })

    # Save messages
    st.session_state.chats[current_chat] = messages

    st.rerun()
