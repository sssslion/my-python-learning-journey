import streamlit as st
import os
import re
import datetime
from openai import OpenAI
from dotenv import load_dotenv



load_dotenv()

app_password = os.getenv("APP_PASSWORD")
if not app_password:

    try:
        app_password = st.secrets["APP_PASSWORD"]
    except Exception:

        st.error("系统错误，请联系管理员。")

        st.stop()

if "password_corret" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    st.title("请输入访问密码")
    pwd = st.text_input("密码", type="password")

    if pwd == app_password:
        st.session_state.password_correct = True
        st.rerun()
    elif pwd:
        st.error("密码错误，请重试！")

else:

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:

        try:
            api_key = st.secrets["DEEPSEEK_API_KEY"]
        except Exception:
            pass
        
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )



    st.set_page_config(page_title="全能AI助理", page_icon="🤖")
    st.title("🤖 我的全能AI助理")



    system_prompt = """你是一个全能助理，拥有以下四个本地工具。
    请根据用户的话，判断该用哪个工具，并严格按照以下格式输出（不要加任何多余的标点）：
    1.如果要算数学题，输出【CALC 算式】
    2.如果要问时间，输出：【TIME】
    3.如果要记事情，输出【SAVE 内容】
    4.如果要看记事本，输出：【READ】
    5.如果不需要工具，请正常聊天回复。
    """


    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": system_prompt}]



    for message in st.session_state.messages:
        if message["role"] != "system":

            content = message["content"]

            if content.startswith("【") or content.startswith("系统工具返回的结果是"):
                continue
            
            with st.chat_message(message["role"]):
                st.write(content)


    if prompt := st.chat_input("你想说点什么？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
                print("即将发给API的数据")
                print(st.session_state.messages)
                print("===")
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=st.session_state.messages,
                    stream=True
                )

                message_placeholder = st.empty()
                answer = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        answer += chunk.choices[0].delta.content

                        message_placeholder.markdown(answer + "▌")

                tool_result = ""
                if "CALC" in answer:
                    answer_fixed = answer.replace("×", "*").replace("÷", "/")
                    expression = "".join(re.findall(r'[0-9+\-*/(). ]', answer_fixed))
                    try:
                        tool_result = f"计算结果为: {eval(expression)}"
                    except Exception as e:
                        tool_result = f"计算出错: {e}"

                elif "TIME" in answer:
                    tool_result = f"当前时间是: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                elif "SAVE" in answer:
                    content_to_save = answer.split("SAVE")[-1].replace("】", "").replace(":", "").replace("：", "").strip()
                    try:
                        with open("全能助理记事本.txt", "a", encoding="utf-8") as f:
                            f.write(content_to_save + "\n")
                        tool_result = f"成功计入记事本，内容是: {content_to_save}"
                    except Exception as e:
                        tool_result = f"写入出错: {e}"

                elif "READ" in answer:
                    try:
                        with open("全能助理记事本.txt", "r", encoding="utf-8") as f:
                            tool_result = f"记事本里的内容是: \n{f.read()}"
                    except FileNotFoundError:
                        tool_result = "记事本目前是空的。"

                if tool_result:

                    message_placeholder.info(f"正在调用工具...\n\n`{tool_result}`")

                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    st.session_state.messages.append({"role": "user", "content": f"系统工具返回的结果是: {tool_result}, 请用自然语言回复我。"})

                    final_response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=st.session_state.messages,
                        stream=True
                    )

                    final_answer = st.write_stream(chunk.choices[0].delta.content or "" for chunk in final_response)

                    st.session_state.messages.append({"role": "assistant", "content": final_answer})

                else:

                    message_placeholder.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})