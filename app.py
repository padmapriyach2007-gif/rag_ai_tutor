import streamlit as st
import google.generativeai as genai
import time
import os

# --------------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------------
st.set_page_config(
    page_title="Quantum AI Tutor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------
# GEMINI API SETUP
# --------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            "You are an expert Quantum Computing AI Tutor. Explain complex topics "
            "like qubits, quantum gates, superposition, entanglement, and Qiskit "
            "clearly and accurately. Use clear formatting, LaTeX for mathematical formulas "
            "where appropriate, and step-by-step code blocks for Qiskit examples."
        )
    )
else:
    model = None

# --------------------------------------------------------
# CUSTOM CSS STYLING
# --------------------------------------------------------
st.markdown("""
<style>
    /* Dark Quantum Theme Colors */
    :root {
        --bg-color: #0d1117;
        --sidebar-bg: #161b22;
        --accent-purple: #7c4dff;
        --accent-blue: #00e5ff;
        --text-color: #c9d1d9;
    }

    /* Sidebar Custom Styling */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid #30363d;
    }

    /* Sidebar Dividers */
    .side-divider {
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #30363d;
    }

    /* Input Trigger Section Styling */
    .input-topics-bar {
        margin-top: 15px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------------
if "chats" not in st.session_state:
    st.session_state.chats = {
        "Default Chat": [
            {
                "role": "assistant",
                "content": "Hello! I am your Quantum AI Tutor. Ask me anything about Quantum Computing, Qubits, Quantum Gates, or Qiskit!"
            }
        ]
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Default Chat"

# Ensure current chat key exists
if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat] = []

# Helper function to process prompt selections
def trigger_learning_prompt(prompt_text):
    st.session_state.chats[st.session_state.current_chat].append(
        {"role": "user", "content": prompt_text}
    )
    if model:
        try:
            response = model.generate_content(prompt_text)
            st.session_state.chats[st.session_state.current_chat].append(
                {"role": "assistant", "content": response.text}
            )
        except Exception as e:
            st.session_state.chats[st.session_state.current_chat].append(
                {"role": "assistant", "content": f"Error generating response: {str(e)}"}
            )
    else:
        st.session_state.chats[st.session_state.current_chat].append(
            {
                "role": "assistant", 
                "content": f"**API Key Warning:** Please set `GEMINI_API_KEY` to receive live responses for: *'{prompt_text}'*"
            }
        )
    st.rerun()

# --------------------------------------------------------
# SIDEBAR NAVIGATION (LOGOUT IS NOW THE FINAL ITEM)
# --------------------------------------------------------
with st.sidebar:
    st.title("⚛️ Quantum AI")
    st.caption("Interactive Quantum Computing Tutor")
    
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    
    # --- CHAT MANAGEMENT ---
    st.subheader("💬 Conversations")
    
    new_chat_name = st.text_input("New Chat Name", placeholder="e.g., Qiskit Basics")
    if st.button("➕ Create New Chat", use_container_width=True):
        if new_chat_name.strip():
            chat_title = new_chat_name.strip()
            if chat_title not in st.session_state.chats:
                st.session_state.chats[chat_title] = [
                    {"role": "assistant", "content": f"Started continuous session: **{chat_title}**."}
                ]
            st.session_state.current_chat = chat_title
            st.rerun()

    # Chat selector dropdown
    chat_list = list(st.session_state.chats.keys())
    selected_chat = st.selectbox(
        "Select Chat", 
        options=chat_list, 
        index=chat_list.index(st.session_state.current_chat)
    )
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    # --- LOGOUT BUTTON (NOTHING UNDERNEATH) ---
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --------------------------------------------------------
# MAIN CHAT INTERFACE
# --------------------------------------------------------
st.header(f"💬 {st.session_state.current_chat}")

if not api_key:
    st.warning("⚠️ `GEMINI_API_KEY` environment variable is missing. Set it to activate real-time Gemini AI responses.")

# Render existing message history
current_messages = st.session_state.chats[st.session_state.current_chat]
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------------
# PROMPT AREA WITH POPOVER TOPICS SYMBOL
# --------------------------------------------------------
st.markdown('<div class="input-topics-bar"></div>', unsafe_allow_html=True)

# Topic Popover Symbol Button next to/above prompt area
pop_col, _ = st.columns([0.25, 0.75])
with pop_col:
    with st.popover("💡 Learning Topics", use_container_width=True):
        st.markdown("### 🧠 LEARNING MODE")
        st.caption("Click any topic to ask the AI tutor instantly:")
        
        topics = [
            ("⚛️ Quantum Computing", "What is Quantum Computing?"),
            ("🔵 Qubits", "What is a Qubit and how does it work?"),
            ("〰️ Quantum Gates", "Explain Quantum Gates with examples."),
            ("🧪 Qiskit", "How do I get started with Qiskit?")
        ]
        
        for label, prompt_text in topics:
            if st.button(label, key=f"input_symbol_{label}", use_container_width=True):
                trigger_learning_prompt(prompt_text)

# Input Box
user_input = st.chat_input("Ask anything about quantum computing...")

if user_input:
    # Display user query in UI
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chats[st.session_state.current_chat].append(
        {"role": "user", "content": user_input}
    )

    # Generate assistant response
    with st.chat_message("assistant"):
        if model:
            try:
                with st.spinner("Thinking..."):
                    response = model.generate_content(user_input)
                    assistant_response = response.text
                    st.markdown(assistant_response)
            except Exception as e:
                assistant_response = f"An error occurred: {str(e)}"
                st.error(assistant_response)
        else:
            assistant_response = "Gemini API Key is not set. Please set the `GEMINI_API_KEY` environment variable to receive automated responses."
            st.warning(assistant_response)

    # Save response to history
    st.session_state.chats[st.session_state.current_chat].append(
        {"role": "assistant", "content": assistant_response}
    )
