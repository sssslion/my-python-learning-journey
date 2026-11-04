from openai import OpenAI
#1.输入密钥
client = OpenAI(
    api_key="miyao",
    base_url="https://api.deepseek.com"
)

try:
    with open("我的笔记.txt","r",encoding="utf-8") as f:
        file_content = f.read()
    print("√ 成功读取本地笔记！")
except Exception as e:
    print("❌ 读取文件失败，请检查文件是否存在：", e)
    file_content = ""

system_prompt = f"你是一个AI助手。请根据以下参考资料回答我的问题： \n{file_content}"

messages = [
    {"role":"system","content": system_prompt}
]

print("==== 专属助理已启动！输入'quit'退出 ====")
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