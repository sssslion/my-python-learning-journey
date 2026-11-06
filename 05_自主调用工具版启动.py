import re
from openai import OpenAI

client = OpenAI(
    api_key="miyao",
    base_url="https://api.deepseek.com"
)

system_prompt = """你是一个聪明的AI助手。你目前拥有一个本地计算器工具。
当你遇到数学计算题时，请【不要】直接回答答案，而是必须严格按照一下格式输出：
【CALC：数学表达式】
例如，如果用户问 5＋5，你只输出：[CALC:5+5]
如果不涉及计算，请正常回答。"""

messages = [{"role": "system","content":system_prompt}]
print("==== 05_自主调用工具版启动 ====")

while True:
    user_input = input("\n你：")
    if user_input.lower() == 'quit':
        break

    messages.append({"role": "user","content": user_input})
    print("AI 正在思考中…")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    answer = response.choices[0].message.content

    if "CALC" in answer:
        print(f"🤖 发现AI发来的工具调用指令： {answer}")

        
        clean_expression = "".join(re.findall(r'[0-9+\-*/(). ]', answer))
        print(f"提取到的纯算式是: [{clean_expression}]")

        try:

            result = eval(clean_expression)
            print(f"🔨 本地计算器算出结果：{result}")


            messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "user", "content": f"计算器返回的结果是：{result},请用自然语言回答我。"})

            final_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            final_answer = final_response.choices[0].message.content
            print(f"AI: {final_answer}")

            messages.append({"role": "assistant", "content": final_response.choices[0].message.content})

        except Exception as e:
            print(f"❌ 计算出错：{e}")
    else:

        print(f"AI: {answer}")
        messages.append({"role": "assistant", "content": answer})