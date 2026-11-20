from openai import Openai
client = Openai(
    api_key="sk-52e99ed10c95450ba568ab36e47f0df8",
    base_url="https://api.deepseek.com"
)

user_queation = "你好，请用一句话介绍一下你。"

print("正在思考…")
response = client.chat.completion.create(
    model="deepseek-chat",
    message=[
        {"role":"user","content": user_question}
    ]
)

answer = response.choices[0].message.content
print("AI 回答：", answer)