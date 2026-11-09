import re
import datetime
from openai import OpenAI

client = OpenAI(
    api_key="miyao",
    base_url="https://api.deepseek.com"
)


system_prompt = """你是一个全能助理，拥有一下四个本地工具。
请根据用户的话，判断该用哪个工具，并严格按照一下格式输出（不要加任何多余的标点）：
1.如果要算数学题，输出【CALC 算式】
2.如果问时间，输出：【TIME】
3.如果要记事情，输出：【SAVE 内容】
4.如果要看记事本，输出：【READ】
5.如果不需要工具，请正常聊天回复。
"""


messages = [{"role": "system", "content": system_prompt}]
print("==== 07_全能调度助理启动 ====")

while True:
    user_input = input("\n你：")
    if user_input.lower() == 'quit':
        break


    messages.append({"role": "user", "content": user_input})
    print("AI 正在思考中…")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )


    answer = response.choices[0].message.content
    tool_result = ""


    if "CALC" in answer:
        print(f"🤖 [调度中心] 识别到计算指令：{answer}")

        answer_fixed = answer.replace("×", "*").replace("÷", "/")

        expression = "".join(re.findall(r'[0-9+\-*/(). ]', answer))
        try:
            tool_result = f"计算结果为：{eval(expression)}"
        except Exception as e:
            tool_result = f"计算出错：{e}"


    elif "TIME" in answer:
        print(f"🤖 [调度中心] 识别到时间指令：{answer}")
        tool_result = f"当前时间是：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


    elif "SAVE" in answer:
        print(f"🤖 [调度中心] 识别到记录指令：{answer}")
        content_to_save = answer.split("SAVE")[-1].replace("】", "").replace(":", "").replace(":", "").strip()
        try:
            with open("全能助理记事本.txt", "a", encoding="utf-8") as f:
                f.write(content_to_save + "\n")
            tool_result = f"成功计入记事本，内容是： {content_to_save}"
        except Exception as e:
            tool_result = f"写入出错：{e}"


    elif "READ" in answer:
        print(f"🤖 [调度中心] 识别到阅读指令：{answer}")
        try:
            with open("全能助理记事本.txt", "r", encoding="utf-8") as f:
                tool_result = f"记事本里的内容是：\n{f.read()}"
        except FileNotFoundError:
            tool_result = "记事本目前是空的。"


    if tool_result:
        print(f"[本地工具] {tool_result}")


        messages.append({"role": "assistant", "content": answer})
        messages.append({"role": "user", "content": f"系统工具返回的结果是：{tool_result}, 请用自然语言回复我。"})


        final_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        final_answer = final_response.choices[0].message.content
        print(f"AI {final_answer}")
        messages.append({"role": "assistant", "content": final_answer})



    else:
        print(f"AI: {answer}")
        messages.append({"role": "assistant", "content": answer})