import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv



load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)



st.set_page_config(page_title="全能AI助理", page_icon="🤖")
st.title("🤖 我的全能AI助理")



if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一个非常有用的AI助手。"}
    ]


for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(mesage["content"])


if prompt := st.chat_input("你想说点什么？"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)



    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages,
            stream=True
        )



        full_response = st.write_stream(chunk.choices[0].delta.content or "" for chunk in response)



    st.session_state.messages.append({"role": "assistant", "content": full_response})