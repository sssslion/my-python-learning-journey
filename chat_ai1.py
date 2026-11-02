from openai import OpenAI
#1.输入密钥
client = OpenAI(
    api_key="sk-bc788925d04b4af598e22b839bece2a2",
    base_url="https://api.deepseek.com"
)
#建立列表，用来保存聊天记录
messages = [
    {"role":"system","content":"你是一个非常有用的AI助手。"}
]

print("==== 聊天机器人已启动！输入'quit'退出 ====")
#开启一个无限循环，让它跟你一直聊
while True:
    user_input = input("\n你：")

    if user_input.lower() == 'quit':
        print("再见！")
        break

    messages.append({"role":"user","content":user_input})
    print("AI 正在思考中…")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    # 提取AI的回答
    answer = response.choices[0].message.content
    print(f"AI:{answer}")

    #[关键一步] 把AI的回答也加进记忆里！
    #如果不加入这一步，AI就记不住它自己刚说了什么
    messages.append({"role":"assistant","content":answer})