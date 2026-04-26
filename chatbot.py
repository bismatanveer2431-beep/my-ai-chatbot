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
#  Custom CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap');
* { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, #f5f5f7 0%, #ffffff 100%); }
h1 { font-size: 2.2rem !important; font-weight: 700 !important; color: #1d1d1f !important; }
.stButton > button {
    border-radius: 20px !important;
    border: 1.5px solid #0071e3 !important;
    color: #0071e3 !important;
    background: white !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { background: #0071e3 !important; color: white !important; }
.mic-box {
    background: linear-gradient(135deg, #e8f0fb, #f0f7ff);
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    border: 1px solid #d0e4ff;
    text-align: center;
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
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# ─────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()

    mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = mode

    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .stApp { background: #1d1d1f !important; color: white !important; }
        h1, h2, h3, p, span { color: white !important; }
        </style>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📎 Upload a File")
    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

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
    st.markdown("### 💾 Chat History")

    if st.session_state.messages:
        chat_text = f"Bisma AI Chatbot — Chat History\nDate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*50}\n\n"
        for msg in st.session_state.messages:
            role = "You" if msg["role"] == "user" else "Bisma AI"
            chat_text += f"{role}:\n{msg['content']}\n\n"

        st.download_button("⬇️ Download Chat (.txt)", data=chat_text,
            file_name=f"bisma_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain")

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.reactions = {}
            st.rerun()
    else:
        st.info("No chat history yet.")

    st.divider()
    st.markdown("<div style='text-align:center;color:#86868b;font-size:12px;'>Built with ❤️ by Bisma<br>Powered by Groq & LLaMA 3.3</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Main UI
# ─────────────────────────────────────────
st.title("🤖 Bisma AI Chatbot")
st.caption("Powered by Groq & LLaMA 3.3 · Built by Bisma")

if st.session_state.pdf_content:
    st.success("📄 File loaded — Ask me anything about it!")

st.divider()

# ─────────────────────────────────────────
#  🎤 REAL VOICE INPUT
# ─────────────────────────────────────────
st.markdown("### 🎤 Voice Input")
st.markdown("<div class='mic-box'><p style='margin:0;color:#0071e3;font-weight:500;'>🎤 Click the button below — speak your message — it converts to text automatically!</p></div>", unsafe_allow_html=True)

try:
    from streamlit_mic_recorder import speech_to_text

    voice_input = speech_to_text(
        language='en',
        start_prompt="🎤 Click to Speak",
        stop_prompt="⏹️ Stop & Send",
        just_once=True,
        use_container_width=True,
        key="stt"
    )

    if voice_input:
        st.session_state.voice_text = voice_input
        st.success(f"✅ You said: **{voice_input}**")

except:
    st.info("🎤 Voice input is loading...")

st.divider()

# ─────────────────────────────────────────
#  Chat Messages + Emoji Reactions
# ─────────────────────────────────────────
EMOJIS = ["👍", "❤️", "😂", "😮", "🔥", "🎉"]

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])

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
prompt = st.chat_input("Type your message here...")

if not prompt and st.session_state.voice_text:
    prompt = st.session_state.voice_text
    st.session_state.voice_text = ""

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    system_prompt = "You are Bisma AI, a helpful, friendly and intelligent assistant built by Bisma. You are powered by Groq and LLaMA 3.3."

    if st.session_state.pdf_content:
        system_prompt += f"\n\nThe user has uploaded a file. Here is its content:\n\n{st.session_state.pdf_content[:8000]}\n\nAnswer questions based on this content."

    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    max_tokens=1024,
                    stream=True
                )
                full_response = ""
                placeholder = st.empty()
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

    st.rerun()
