from openai import OpenAI
import datetime

client = OpenAI(
    api_key="miyao",
    base_url="https://api.deepseek.com"
)

messages = [{"role":"system","content":"你是一个有用的助手。"}]
print("==== 超级助理已启动（带工具版） ====")

while True:
    user_input = input("\n你：")
    if user_input.lower() == 'quit':
        break



    if "几点" in user_input or "时间" in user_input:
        current_time = datetime.datetime.now().strftime("%Y-%m-%D %H:%M:%S")
        print(f"AI (本地工具) : 现在的系统时间是 {current_time}")
        continue


messages.append({"role": "user", "content": user_input})
print("AI 正在思考中…")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

answer = response.choices[0].message.content
print(f"AI:{answer}")
messages.append({"role": "assistant", "content":answer})