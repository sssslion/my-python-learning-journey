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
        print(idx, score)
        scored.append((score, idx))

    scored.sort(reverse=True)
    top = scored[:k]
    return [chunks[i] for _, i in top]


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