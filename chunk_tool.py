import json
import math
import urllib.request
from functools import lru_cache

def split_into_chunks(text, size=300):
    """把一整篇文章切成若干块，每块大约 size 个字。"""
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i + size])
    return chunks
def pick_relevant(chunks, question, k=3):
    """从所有块里挑出问题最相关的 k 块。"""
    quest_chars = set(question)
    scored = []
    for idx, chunk in enumerate(chunks):
        score = len(quest_chars & set(chunk))
        
        scored.append((score, idx))

    scored.sort(key=lambda t: t[0], reverse=True)
    top = scored[:k]
    return [chunks[i] for _, i in top]

def bigrams(text):
    """把一段文字拆成相邻两个字一组的组合，去重"""
    return {text[i:i + 2] for i in range(len(text) - 1)}

def pick_relevant_v2(chunks, question, k=3):
    """和 pick_relevant 一样, 但按"两个字的组合"算分"""
    quest_grams = bigrams(question)
    scored = []
    for idx, chunk in enumerate(chunks):
        score = len(quest_grams & bigrams(chunk))
        scored.append((score, idx))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [chunks[i] for _, i in scored[:k]]

def idf_table(chunks):
    """统计每个二字组合出现在多少块里，算出它的权重"""
    df = {}
    for chunk in chunks:
        for g in bigrams(chunk):
            df[g] = df.get(g, 0) + 1

    n = len(chunks)
    return {g: math.log(n / c) for g, c in df.items()}

def pick_relevant_v3(chunks, question, k=3):
    """v2 的升级版: 不是数命中几个, 而是把他们各自的权重加起来"""
    weights = idf_table(chunks)
    quest_grams = bigrams(question)

    scored = []
    for idx, chunk in enumerate(chunks):
        shared = quest_grams & bigrams(chunk)
        score = sum(weights.get(g,0) for g in shared)
        scored.append((score, idx))

    scored.sort(key=lambda t: t[0], reverse=True)
    return [chunks[i] for _, i in scored[:k]]

@lru_cache(maxsize=None)
def embed(text):
    """把一段文字变成1024个数字（同一个text只算一次）"""
    req = urllib.request.Request(
        "http://localhost:11434/api/embeddings",
        data=json.dumps({"model": "bge-m3", "prompt": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req))["embedding"]

def cosine(a, b):
    """夹角余弦，越大越像"""
    dot = sum(x * y for x, y in zip(a, b))
    la = math.sqrt(sum(x * x for x in a))
    lb = math.sqrt(sum(y * y for y in b))
    return dot / (la * lb)

def pick_relevant_v4(chunks, question, k=3):
    """向量版：不看字面意思，只看意思远近"""
    q_vec = embed(question)
    scored = []
    for idx, chunk in enumerate(chunks):
        score = cosine(q_vec, embed(chunk))
        scored.append((score,idx))


    scored.sort(key=lambda t: t[0], reverse=True)
    return [chunks[i] for _, i in scored[:k]]


if __name__ == "__main__":
   import pypdf

   reader = pypdf.PdfReader(r"D:\claude\chat-ai\yanyujianghu_20261115162114.pdf")
   full = ""
   for page in reader.pages:
       full += page.extract_text() + "\n"

   chunks = split_into_chunks(full)
   print("总字数:", len(full))
   print("块数:", len(chunks))
   print("第一块开头:", chunks[0][:80])

   picked = pick_relevant(chunks, "商昊乾 刀法")
   print("选中的块:", len(picked))
   print(picked[0][:60])