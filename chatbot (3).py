import os
import json
import datetime
import streamlit as st
from groq import Groq
import PyPDF2
import io

# ─────────────────────────────────────────
#  Page Configuration
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Bisma AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─────────────────────────────────────────
#  Custom CSS — Apple-style UI
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #f5f5f7 0%, #ffffff 100%);
}

/* Title */
h1 { 
    font-size: 2.2rem !important; 
    font-weight: 700 !important;
    color: #1d1d1f !important;
}

/* Chat messages */
.stChatMessage {
    border-radius: 18px !important;
    padding: 4px 8px !important;
    margin: 4px 0 !important;
}

/* Input box */
.stChatInputContainer {
    border-radius: 25px !important;
    border: 1.5px solid #d2d2d7 !important;
    background: white !important;
}

/* Buttons */
.stButton > button {
    border-radius: 20px !important;
    border: 1.5px solid #0071e3 !important;
    color: #0071e3 !important;
    background: white !important;
    font-size: 13px !important;
    padding: 4px 16px !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: #0071e3 !important;
    color: white !important;
}

/* Sidebar */
.css-1d391kg { background: #f5f5f7 !important; }

/* File uploader */
.stFileUploader {
    border-radius: 16px !important;
}

/* Success/info messages */
.stSuccess, .stInfo {
    border-radius: 12px !important;
}

/* Emoji reaction bar */
.emoji-bar {
    display: flex;
    gap: 8px;
    margin-top: 4px;
    margin-left: 48px;
}

.emoji-btn {
    background: #f5f5f7;
    border: 1px solid #e0e0e0;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Groq Client
# ─────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ─────────────────────────────────────────
#  Session State
# ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "reactions" not in st.session_state:
    st.session_state.reactions = {}

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# ─────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()

    # Dark / Light Mode Toggle
    mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = mode

    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .stApp { background: #1d1d1f !important; color: white !important; }
        h1, h2, h3, p, span { color: white !important; }
        .stChatInputContainer { background: #2c2c2e !important; border-color: #3a3a3c !important; }
        </style>
        """, unsafe_allow_html=True)

    st.divider()

    # PDF Upload
    st.markdown("### 📎 Upload a File")
    uploaded_file = st.file_uploader(
        "Upload PDF to chat about it",
        type=["pdf", "txt"],
        help="Upload a PDF or text file and ask questions about it!"
    )

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
            st.session_state.pdf_content = pdf_text
            st.success(f"✅ PDF loaded! ({len(pdf_reader.pages)} pages)")
        elif uploaded_file.type == "text/plain":
            st.session_state.pdf_content = uploaded_file.read().decode("utf-8")
            st.success("✅ Text file loaded!")

    if st.session_state.pdf_content:
        if st.button("🗑️ Clear File"):
            st.session_state.pdf_content = ""
            st.rerun()

    st.divider()

    # Download Chat History
    st.markdown("### 💾 Chat History")

    if st.session_state.messages:
        # Plain text download
        chat_text = f"Bisma AI Chatbot — Chat History\n"
        chat_text += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        chat_text += "=" * 50 + "\n\n"
        for msg in st.session_state.messages:
            role = "You" if msg["role"] == "user" else "Bisma AI"
            chat_text += f"{role}:\n{msg['content']}\n\n"

        st.download_button(
            label="⬇️ Download Chat (.txt)",
            data=chat_text,
            file_name=f"bisma_ai_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

        # JSON download
        chat_json = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="⬇️ Download Chat (.json)",
            data=chat_json,
            file_name=f"bisma_ai_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.reactions = {}
            st.rerun()
    else:
        st.info("No chat history yet.")

    st.divider()
    st.markdown("""
    <div style='text-align:center; color: #86868b; font-size: 12px;'>
        Built with ❤️ by Bisma<br>
        Powered by Groq & LLaMA 3.3
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Main Chat UI
# ─────────────────────────────────────────
st.title("🤖 Bisma AI Chatbot")
st.caption("Powered by Groq & LLaMA 3.3 · Built by Bisma")

# Voice Input Info
st.info("🎤 **Voice Input:** Click the microphone icon in the chat box below to speak your message!", icon="🎤")

if st.session_state.pdf_content:
    st.success(f"📄 File loaded — Ask me anything about it!")

st.divider()

# ─────────────────────────────────────────
#  Display Chat Messages + Emoji Reactions
# ─────────────────────────────────────────
EMOJIS = ["👍", "❤️", "😂", "😮", "🔥", "🎉"]

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])

        # Emoji reactions (only for bot messages)
        if message["role"] == "assistant":
            reaction_key = f"reaction_{i}"
            current_reaction = st.session_state.reactions.get(reaction_key, None)

            cols = st.columns(len(EMOJIS) + 1)
            for j, emoji in enumerate(EMOJIS):
                with cols[j]:
                    count = 1 if current_reaction == emoji else 0
                    label = f"{emoji} {count}" if count > 0 else emoji
                    if st.button(label, key=f"emoji_{i}_{j}"):
                        if current_reaction == emoji:
                            del st.session_state.reactions[reaction_key]
                        else:
                            st.session_state.reactions[reaction_key] = emoji
                        st.rerun()

# ─────────────────────────────────────────
#  Chat Input
# ─────────────────────────────────────────
if prompt := st.chat_input("Type your message here... or use 🎤 mic to speak!"):

    # Show user message
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Build messages for API
    system_prompt = "You are Bisma AI, a helpful, friendly and intelligent assistant built by Bisma. You are powered by Groq and LLaMA 3.3."

    if st.session_state.pdf_content:
        system_prompt += f"\n\nThe user has uploaded a file. Here is its content:\n\n{st.session_state.pdf_content[:8000]}\n\nAnswer questions based on this content."

    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    max_tokens=1024,
                    stream=True
                )

                # Streaming response
                full_response = ""
                placeholder = st.empty()
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
    st.rerun()
