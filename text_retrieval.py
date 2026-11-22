from chunk_tool import spilt_into_chunks, pick_relevant

TEXT_FILE = "学习笔记.txt"
SIZE = 600
K = 3

TESTS = [
    ("Streamlit 点一下按钮脚本会执行几次", "重跑"),
    ("set(a) & set(b) 得到的是什么", "交集"),
    ("元组排序并列时谁在前面", "序号大的在前"),
    ("函数忘了写 return 会怎样", "None"),
    ("(5, 2) 和 (5, 10) 排序时谁在前？reverse=True 时呢？", "(5,2)在前"),
    ("", "")
]

def main():
    text = open(TEXT_FILE, encoding="utf-8").read()
    chunks = spilt_into_chunks(text, size=SIZE)
    print("总字数:", len(text), "块数:", len(chunks))

    hit = 0
    for q, keyword in TESTS:
        if not q:
            continue
        picked = pick_relevant(chunks, q, k=K)

        ok = any(keyword in c for c in picked)
        if ok:
            hit += 1
        print(f"\n命中率: {hit}/{len(TESTS)}")

if __name__ == "__main__":
    main()