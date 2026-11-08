import re
from openai import OpenAI

client = OpenAI(
    api_key="miyao",
    base_url="https://api.deepseek.com"
)


system_prompt = """你是一个专属助手，拥有一个本地记事本。
当用户让你“记一下”或者“保存”某件事时，请必须严格按照以下格式输出：
【SAVE 要记录的具体内容】
当用户让你“我记了什么”或者“看看待办”时，请必须严格按照以下格式输出：
【READ】
如果不涉及记录或读取，请正常回答。"""

messages = [{"role":"system", "content": system_prompt}]
print("==== 06_专属记事本Agent1启动 ====")

while True:
    user_input = input("\n你:")
    if user_input.lower() == 'quit':
        break

    messages.append({"role":"user",  "content": user_input})
    print("AI 正在思考中…")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    answer = response.choices[0].message.content


    if "SAVE" in answer:
        print(f"🤖 发现AI发来的记录指令：{answer}")


        content_to_save = answer.replace("【","").replace("】","").replace("SAVE:","").replace("SAVE","").replace(":", "").replace(":", "").strip()
        print(f"提取到要记录的内容是：[{content_to_save}]")

        try:

            with open("我的待办.txt","a", encoding="utf-8") as f:
                f.write(content_to_save + "\n")
            print("已经成功写入本地记事本！")


            messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "user", "content":f"记事本系统已成功保存内容。请用自然语言回复我。"})

            final_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
         )
            final_answer = final_response.choices[0].message.content
            print(f"AI: {final_answer}")
            messages.append({"role": "assistant", "content": final_answer})

        except Exception as e:
            print(f"写入文件出错：{e}")

    elif "READ" in answer:
        print(f"🤖 发现AI发来的读取指令：{answer}")

        try:
            with open("我的待办.txt", "r",encoding="utf-8") as f:
                todo_content = f.read()

            if not todo_content.strip():
                todo_content = " (记事本目前是空的)"

            print(f"🔍 读取到的本地内容：\n{todo_content}")


            messages.append({"role": "assistant", "content":answer})
            messages.append({"role": "user", "content": f"这是记事本的所有内容：\n{todo_content}\n请用自然语言整理后回答我。"})

            final_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            final_answer = final_response.choices[0].message.content
            print(f"AI: {final_answer}")
            messages.append({"role": "assistant", "content": final_answer})

        except FileNotFoundError:
            print("记事本文件不存在，请先记录一些内容。")
        except Exception as e:
            print(f"读取文件出错: {e}")
    else:
        print(f"AI: {answer}")
        messages.append({"role": "assistant", "content": answer})