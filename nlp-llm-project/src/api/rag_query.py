# src/api/rag_query.py (pseudocode)
from openai import OpenAI   # hypothetical
from chromadb import Client
def answer_query(query):
    # 1. embed query -> retrieve docs
    docs = vector_db.query(query, top_k=5)
    context = "\n\n".join([d["text"] for d in docs])
    prompt = f"You are an assistant. Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion:\n{query}\n\nAnswer:"
    resp = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
    return resp.choices[0].message.content
