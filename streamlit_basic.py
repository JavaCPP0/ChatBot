import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()  # Load environment variables from .env file
with st.sidebar:
    api_key = os.getenv("OPENAI_API_KEY")
    "[get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[view the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in Github Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
    

st.title("ChatBot")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
    
if prompt := st.chat_input():
    if not api_key:
        st.info("Please set your OpenAI API key in the .env file.")
        st.stop()

    client = OpenAI(api_key=api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        messages=st.session_state.messages
    )   

    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
        