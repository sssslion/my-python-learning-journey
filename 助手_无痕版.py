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
        pass

is_logged_in = st.session_state.get("logged_in", False)

if not is_logged_in:
    st.title("请输入访问密码")
    pwd = st.text_input("密码", type="password")

    if pwd:

        if pwd.strip() == str(app_password).strip():
            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error(f"密码错误！")
       
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

    with st.sidebar:
        st.header("控制面板")

        uploaded_file = st.file_uploader("上传PDF文档", type=["pdf"])

        if st.button("清空对话记忆"):
            st.session_state.messages = [{"role": "system", "content": system_prompt}]

            if "current_pdf_name" in st.session_state:
                del st.session_state.current_pdf_name
            if "pdf_content" in st.session_state:
                del st.session_state.pdf_content
            st.rerun()

    uploaded_file = st.file_uploader("上传你的PDF文件（让AI帮你读）", type=["pdf"])
    
    if uploaded_file is not None:
        import pypdf
    
        pdf_reader = pypdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"
        pdf_text = pdf_text.encode('utf-8', 'ignore').decode('utf-8')
    
        if "current_name" not in st.session_state or st.session_state.current_pdf_name != uploaded_file.name:

            st.session_state.current_pdf_name = uploaded_file.name

            st.session_state.pdf_content = pdf_text

            new_system_prompt = f"""你是一个专业的文档阅读助手。
            请严格根据用户上传的文档内容回答问题。如果文档里没有写，请直接说“文档未提及”。
            以下是文档内容:
            {pdf_text[:8000]}
            """

            st.session_state.messages = [{"role": "system", "content": new_system_prompt}]

            st.success(f"文档《{uploaded_file.name}》读取成功，聊天记忆已刷新！")



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