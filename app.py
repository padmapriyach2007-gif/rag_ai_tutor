import streamlit as st


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

    /* =========================
       MAIN APP
       ========================= */

    .stApp {
        background-color: #07091a;
    }

    [data-testid="stMain"] {
        background-color: #07091a;
    }


    /* =========================
       SIDEBAR
       ========================= */

    [data-testid="stSidebar"] {
        background-color: #08091b;
    }

    [data-testid="stSidebar"] h1 {
        color: white;
    }


    /* =========================
       BUTTONS
       ========================= */

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 8px;
        min-height: 42px;
        background-color: #292b37;
        border: 1px solid #3c3e50;
        color: white;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #363847;
        border-color: #6c63ff;
    }


    /* =========================
       HERO
       ========================= */

    .hero-box {
        background-color: #191b25;
        border: 1px solid #292c3a;
        border-radius: 15px;
        padding: 55px 20px;
        text-align: center;
        margin-top: 25px;
        margin-bottom: 25px;
    }

    .hero-icon {
        font-size: 48px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 700;
        color: white;
        margin-top: 10px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #aeb1c5;
        margin-top: 10px;
    }

    .online {
        color: #42e88b;
        font-size: 14px;
        margin-top: 18px;
    }


    /* =========================
       LEARNING BOX
       ========================= */

    .learning-box {
        background-color: #10294e;
        border: 1px solid #193d70;
        border-radius: 10px;
        padding: 16px;
        margin-top: 20px;
    }


    /* =========================
       LOGIN
       ========================= */

    .login-box {
        max-width: 550px;
        margin: 100px auto;
        background-color: #191b25;
        border: 1px solid #292c3a;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
    }

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# QUANTUM AI RESPONSE
# ============================================================

def quantum_response(question):

    q = question.lower().strip()

    if "qubit" in q:

        return """
### ⚛️ What is a Qubit?

A **qubit** is the basic unit of quantum information.

A classical bit can have either:

**0 or 1**

A qubit can exist in a combination of both states:

**|ψ⟩ = α|0⟩ + β|1⟩**

This property is called **superposition**.
"""

    elif "superposition" in q:

        return """
### 🌌 Superposition

Superposition means a quantum system can exist in a combination
of multiple possible states.

For example:

**|ψ⟩ = α|0⟩ + β|1⟩**

When the qubit is measured, we obtain either **0 or 1**.
"""

    elif "entanglement" in q:

        return """
### 🔗 Quantum Entanglement

Quantum entanglement occurs when two or more qubits become
strongly correlated.

The state of one qubit is related to the state of another,
even when they are separated.
"""

    elif "hadamard" in q:

        return """
### H Gate — Hadamard Gate

The **Hadamard gate** is used to create superposition.

For example:

**H|0⟩ = (|0⟩ + |1⟩) / √2**

It is one of the most important quantum gates.
"""

    elif "cnot" in q:

        return """
### CNOT Gate

**CNOT** means Controlled-NOT.

It contains:

• Control qubit  
• Target qubit

The target qubit is flipped when the control qubit is **1**.
"""

    elif "qiskit" in q:

        return """
### 🐍 Qiskit

**Qiskit** is a Python framework for quantum computing.

It can be used to:

• Create quantum circuits
• Apply quantum gates
• Simulate circuits
• Run quantum programs
"""

    elif "gate" in q:

        return """
### ⚙️ Quantum Gates

Some common quantum gates are:

• **X gate** — Quantum NOT
• **Y gate**
• **Z gate**
• **H gate** — Creates superposition
• **S gate**
• **T gate**
• **CNOT** — Controlled operation
"""

    elif q in ["hi", "hello", "hey"]:

        return """
### 👋 Hello!

I'm your **Quantum AI Tutor**.

You can ask me about:

• Qubits
• Superposition
• Entanglement
• Quantum Gates
• Quantum Circuits
• Qiskit
"""

    else:

        return f"""
### ⚛️ Quantum AI Tutor

You asked:

**{question}**

I can help you learn about quantum computing.

Try asking:

**What is a qubit?**

or

**What is superposition?**
"""


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        """
<div class="login-box">
    <div class="hero-icon">⚛️</div>
    <h1>Quantum Lab</h1>
    <p>AI-Powered Learning Space</p>
</div>
""",
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

    st.title("⚛️ QUANTUM LAB")

    st.caption("AI-Powered Learning Space")


    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    st.markdown("---")

    st.write("👤 **Logged In**")

    st.caption(st.session_state.user_email)


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "➕ New Chat",
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


    # --------------------------------------------------------
    # YOUR CHATS
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader("💬 Your Chats")


    chat_names = list(st.session_state.chats.keys())

    for chat_name in chat_names:

        is_current = (
            chat_name == st.session_state.current_chat
        )

        button_text = (
            f"🟣 {chat_name}"
            if is_current
            else f"💬 {chat_name}"
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

    st.markdown("---")

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


    # --------------------------------------------------------
    # DELETE CURRENT CHAT
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "🗑️ Delete Current Chat",
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


    # --------------------------------------------------------
    # CLEAR CONVERSATION
    # --------------------------------------------------------

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True
    ):

        current_name = st.session_state.current_chat

        st.session_state.chats[current_name] = []

        st.toast("Conversation cleared!")

        st.rerun()


    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.rerun()


    # --------------------------------------------------------
    # LEARNING MODE
    # --------------------------------------------------------

    st.markdown("---")

    st.info(
        """
🧠 **Learning Mode**

Ask questions about:

• Quantum Computing

• Qubits

• Quantum Gates

• Qiskit
        """
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


if question:

    # User message
    messages.append({
        "role": "user",
        "content": question
    })

    # AI response
    answer = quantum_response(question)

    messages.append({
        "role": "assistant",
        "content": answer
    })

    # Save
    st.session_state.chats[current_chat] = messages

    st.rerun()
