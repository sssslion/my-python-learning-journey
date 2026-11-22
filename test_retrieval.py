from chunk_tool import split_into_chunks, pick_relevant_v3 as pick_relevant

TEXT_FILE = "学习笔记.txt"
SIZE = 600
K = 3

TESTS = [
    ("Streamlit 点一下按钮脚本会执行几次", "重跑"),
    ("set(a) & set(b) 得到的是什么", "交集"),
    ("元组排序并列时谁在前面", "序号大的在前"),
    ("函数忘了写 return 会怎样", "函数返回 None"),
    ("(5, 2) 和 (5, 10) 排序时谁在前？reverse=True 时呢？", "序号大的在前"),
    ("AttributeError 报出来时，它前面的代码执行了吗？", "它前面的行已经跑过了"),
    ("git status 里 ?? 和 !! 分别是什么意思？", "被 .gitignore 挡住了"),
]

def main():
    text = open(TEXT_FILE, encoding="utf-8").read()
    text = text.split("第七部分")[0]
    chunks = split_into_chunks(text, size=SIZE)
    print("总字数:", len(text), "块数:", len(chunks))

    hit = 0
    for q, keyword in TESTS:
        if not q:
            continue
        picked = pick_relevant(chunks, q, k=K)

        gold = [i for i, c in enumerate(chunks) if keyword in c]
        if len(gold) !=1:
            print("跳过（关键词不唯一）:", q)
            continue

        rank = 0
        for r, p in enumerate(picked, start=1):
            if chunks.index(p) == gold[0]:
                rank = r

        if rank:
            hit += 1
            print(f"第{rank}名  {q}")
        else:
            print(f"没进前{K}  {q}")

if __name__ == "__main__":
    main()