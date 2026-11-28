import json
from chunk_tool import split_into_chunks, pick_relevant_v3, pick_relevant_v4

CORPUS = r"D:\claude\项目5-毛主席对话\知识库\篇.json"
SIZE = 600
K = 3
MAX_I = 100

TESTS = [
    ("为什么说认清敌友是革命的首要问题", "中国社会各阶级的分析"),
    ("人的正确认识是从哪里来的", "实践论"),
    ("矛盾的普遍性和特殊性是什么关系", "矛盾论"),
    ("抗日战争会经历哪几个阶段", "论持久战"),
    ("为什么说没有调查就没有发言权", "反对本本主义"),
    ("愚公移山讲了什么道理", "愚公移山"),
    ("星星之火可以燎原这个比喻是什么意思", "星星之火，可以燎原"),
    # —— A 组：原句题（问题里用了文章的原词，v3 该占优）——
    ("自由主义有哪几种表现", "反对自由主义"),
    ("党八股有哪几条罪状", "反对党八股"),
    ("工农武装割据需要具备哪些条件", "井冈山的斗争"),
    ("劳动英雄有哪三种作用", "必须学会做经济工作"),
    ("白求恩身上体现的是什么精神", "纪念白求恩"),
    ("五四运动比辛亥革命进步在哪里", "五四运动"),
    # —— B 组：改写题（同一个意思，换词问，v4 该占优）——
    ("一个外国人为什么值得全体共产党员学习", "纪念白求恩"),
    ("机关干部怎么才能真正了解下面的真实情况", "《农村调查》的序言和跋"),
    ("为什么部队除了打仗还要自己种地", "组织起来"),
    ("领导怎么才能把一个单位的工作抓出成效", "关于领导方法的若干问题"),
    ("抗日战争时期对地主和资本家应该怎么办", "论政策"),
    ("为什么在中国的半殖民地条件下红色政权能够生存下来", "中国的红色政权为什么能够存在？"),
]

def build():
    data = json.load(open(CORPUS, encoding="utf-8"))
    chunks, titles = [], []
    for art in data:
        if art["i"] >=MAX_I:
            continue
        text = "\n".join(art["段"])
        for c in split_into_chunks(text, size=SIZE):
            chunks.append(c)
            titles.append(art["标题"])
    return chunks, titles

def run(fn, name, chunks, titles):
    print(f"\n=== {name} ===")
    hit = 0
    for q, gold in TESTS:
        picked = fn(chunks, q, k=K)
        got = [titles[chunks.index(p)] for p in picked]
        ok = gold in got
        hit += ok
        print(("√" if ok else "×"), q, "→", got)
    print(f"{name}: {hit}/{len(TESTS)}")

if __name__ == "__main__":
    chunks, titles = build()
    print("块数:", len(chunks))
    run(pick_relevant_v3, "v3 IDF", chunks, titles)
    run(pick_relevant_v4, "v4 向量", chunks, titles)