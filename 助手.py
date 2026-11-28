import streamlit as st
import os
import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv
from chunk_tool import split_into_chunks, pick_relevant_v3 as pick_relevant



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



    # ============ 四个真正的工具函数 ============

    def calculator(expression):
        """只允许数字和四则运算符，别的一律拒掉"""
        allowed = "0123456789+-*/(). "
        if any(c not in allowed for c in expression):
            return "算式里有不允许的字符"
        try:
            return eval(expression)
        except Exception as e:
            return f"算不出来: {e}"


    def get_time():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def save_note(content):
        with open("全能助理记事本.txt", "a", encoding="utf-8") as f:
            f.write(content + "\n")
        return f"已经记到记事本: {content}"


    def read_note():
        try:
            with open("全能助理记事本.txt", encoding="utf-8") as f:
                return f.read().strip() or "记事本是空的"
        except FileNotFoundError:
            return "记事本是空的"


    # ============ 给模型看的说明书 ============

    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "计算数学表达式，例如 (12+8)*3/5",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "要计算的算式"}
                    },
                    "required": ["expression"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "获取当前的日期和时间",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "save_note",
                "description": "往记事本里写一条新内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "要记下的内容"}
                    },
                    "required": ["content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_note",
                "description": "读出记事本里已有的全部内容",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]


    # ============ 分发：名字 → 函数 ============

    def run_tool(name, arguments):
        args = json.loads(arguments)
        if name == "calculator":
            return calculator(args["expression"])
        if name == "get_time":
            return get_time()
        if name == "save_note":
            return save_note(args["content"])
        if name == "read_note":
            return read_note()
        return f"没有这个工具: {name}"


    system_prompt = "你是一个全能助理，可以聊天，也可以调用工具帮用户算数、查时间、记事情。回答用中文，简洁一点。"


    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": system_prompt}]

    with st.sidebar:
        st.header("控制面板")


        if st.button("清空对话记忆"):
            st.session_state.messages = [{"role": "system", "content": system_prompt}]

            if "current_pdf_name" in st.session_state:
                del st.session_state.current_pdf_name
            if "pdf_chunks" in st.session_state:
                del st.session_state.pdf_chunks
            st.rerun()

    uploaded_file = st.file_uploader("上传你的PDF文件（让AI帮你读）", type=["pdf"])

    if uploaded_file is not None:
        import pypdf

        pdf_reader = pypdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"
        pdf_text = pdf_text.encode('utf-8', 'ignore').decode('utf-8')

        if st.session_state.get("current_pdf_name") != uploaded_file.name:
            st.session_state.current_pdf_name = uploaded_file.name
            st.session_state.pdf_chunks = split_into_chunks(pdf_text, size=600)
            st.session_state.messages = [{"role": "system", "content": system_prompt}]
            st.success(f"文档《{uploaded_file}》读取成功，切成了{len(st.session_state.pdf_chunks)}块")



    for message in st.session_state.messages:
        if message["role"] != "system":

            with st.chat_message(message["role"]):
                st.write(message["content"])


    if prompt := st.chat_input("你想说点什么？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            msgs = list(st.session_state.messages)

            if st.session_state.get("pdf_chunks"):
                picked = pick_relevant(st.session_state.pdf_chunks, prompt, k=3)
                msgs.append({
                    "role": "system",
                    "content": "以下是文档中与问题最相关的片段，请根据它们回答: \n\n" + "\n\n".join(picked)
                })

            answer = ""
            for step in range(5):
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=msgs,
                    tools=TOOLS,
                )
                msg = response.choices[0].message

                if not msg.tool_calls:
                    answer = msg.content or ""
                    break

                msgs.append(msg)

                for tc in msg.tool_calls:
                    st.caption(f"🔧 调用 {tc.function.name}({tc.function.arguments})")
                    result = run_tool(tc.function.name, tc.function.arguments)
                    msgs.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result),
                    })
            else:
                answer = "工具调用次数太多了，先停一下。"

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
