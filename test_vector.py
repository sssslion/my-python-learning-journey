import json
import math
import urllib.request

def embed(text):
    """把一段文字变成1024个数字"""
    req = urllib.request.Request(
        "http://localhost:11434/api/embeddings",
        data=json.dumps({"model": "bge-m3", "prompt": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req))["embedding"]

def cosine(a,b):
    """算两个向量的夹角余弦，越接近1越像"""
    dot = sum(x * y for x,y in zip(a,b))
    la = math.sqrt(sum(x * x for x in a))
    lb = math.sqrt(sum(y * y for y in b))
    return dot / (la * lb)

if __name__ == "__main__":
    base = embed("XRD 峰拟合")
    for t in ["衍射峰的分解", "曲线拟合", "苹果手机", "今天天气不错"]:
        print(round(cosine(base, embed(t), ), 3), t)