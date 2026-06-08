#src/backend/app/rag.py
import os
import google.generativeai as genai
from chromadb import HttpClient
from pypdf import PdfReader

# Gemini APIキーの設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ChromaDBクライアントの初期化（埋め込み関数なし・embeddings直接渡し）
chroma_client = HttpClient(
    host=os.environ.get("CHROMA_HOST", "vectordb"),
    port=int(os.environ.get("CHROMA_PORT", 8000))
)
collection = chroma_client.get_or_create_collection(name="pdf_documents")

# Gemini生成モデル（回答生成用）
generation_model = genai.GenerativeModel("gemini-1.5-flash")


def get_embedding(text: str, task_type: str = "retrieval_document") -> list:
    """Gemini text-embedding-004でテキストをベクトル化"""
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type=task_type
    )
    return result["embedding"]


def extract_and_store_pdf(pdf_path: str, document_id: str) -> int:
    """1. PDFからテキストを抽出してChromaへ格納"""
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    # テキストをチャンク分割（chunk_size=500, overlap=100）
    chunks = [full_text[i:i+500] for i in range(0, len(full_text), 400)]

    if not chunks:
        return 0

    # チャンクごとにGemini text-embedding-004でベクトル化
    embeddings = []
    for chunk in chunks:
        embedding = get_embedding(chunk, task_type="retrieval_document")
        embeddings.append(embedding)

    # ChromaDBに登録（embeddingsを直接渡す）
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"{document_id}_{i}" for i in range(len(chunks))]
    )
    return len(chunks)


def answer_with_rag(user_query: str) -> str:
    """2. ユーザーの質問に対してRAGで回答生成"""
    # Gemini text-embedding-004でクエリをベクトル化して検索
    query_embedding = get_embedding(user_query, task_type="retrieval_query")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    context = "\n".join(results['documents'][0]) if results['documents'] else ""

    # Gemini用のプロンプト構築
    prompt = f"""以下の参考資料に基づいて、ユーザーの質問に答えてください。

【参考資料】
{context}

【質問】
{user_query}
"""

    # Gemini API呼び出し（gemini-1.5-flash）
    response = generation_model.generate_content(prompt)
    return response.text
