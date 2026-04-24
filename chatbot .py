import os
# ============================================
# PROFESSIONAL CHATBOT WITH UI - VS CODE
# ============================================

import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Title
st.title("🤖 My AI Chatbot")
st.write("Powered by Groq & LLaMA | Built by Bisma")

# Your Groq API Key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))  # <-- CHANGE THIS ONLY

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. You are friendly, smart and helpful."
        }
    ]

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# User input box
user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.write(user_input)

    # Add to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Get bot response
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )
        bot_reply = response.choices[0].message.content

    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    # Show bot response
    with st.chat_message("assistant"):
        st.write(bot_reply)

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })
