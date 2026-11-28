import datetime
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

NOTE_FILE = "全能助理记事本.txt"

def calculator(expression):
    """真正的计算器函数：模型只负责把算式传进来，算不算、怎么算有我们决定。"""
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
    with open(NOTE_FILE, "a", encoding='utf-8') as f:
        f.write(content + "\n")
    return f"已经记到记事本: {content}"

def read_note():
    try:
        with open(NOTE_FILE, encoding="utf-8") as f:
            return f.read().strip() or "记事本是空的"
    except FileNotFoundError:
        return "记事本是空的"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，例如(12+8)*3/5",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的算式，只允许数字和 + - * / ( ) 和小数点"
                    },
                },
                "required": ["expression"]
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
            "decription": "往记事本里写一条新内容",
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
        "function":{
            "name": "read_note",
            "description": "读出记事本里已有的全部内容",
            "parameters": {"type": "object", "properties": {}},
        },
    },

]

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

def ask(question):
    print(f"\n{'=' * 40}\n问: {question}")
    messages = [{"role": "user", "content": question}]

    for step in range(3):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            print("答:", msg.content)
            break

        print(f"第{step + 1}轮 要调 {len(msg.tool_calls)}个工具")
        messages.append(msg)

        for tc in msg.tool_calls:
            print("  -", tc.function.name, tc.function.arguments)
            result = run_tool(tc.function.name, tc.function.arguments)
            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": str(result)}
            )

if __name__ == "__main__":
    for q in [
        "现在几点了？",
        "帮我记一下：明天下午打游戏",
        "现在几点？把这个时间也记到记事本里",
        "我记事本里有什么？",
    ]:
        ask(q)