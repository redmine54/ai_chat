#src/backend/app/rag.py
import os
import anthropic
from chromadb import HttpClient
from pypdf import PdfReader

# 各種クライアントの初期化（環境変数から取得）
claude_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
chroma_client = HttpClient(
    host=os.environ.get("CHROMA_HOST", "vectordb"),
    port=int(os.environ.get("CHROMA_PORT", 8000))
)
collection = chroma_client.get_or_create_collection(name="pdf_documents")

def extract_and_store_pdf(pdf_path: str, document_id: str):
    """1. PDFからテキストを抽出してChromaへ格納"""
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    # テキストをチャンク分割
    chunks = [full_text[i:i+500] for i in range(0, len(full_text), 400)]

    # ベクトルDBに登録（Chromaがデフォルトの埋め込みモデルを適用）
    collection.add(
        documents=chunks,
        ids=[f"{document_id}_{i}" for i in range(len(chunks))]
    )
    return len(chunks)

def answer_with_rag(user_query: str) -> str:
    """2. ユーザーの質問に対してRAGで回答生成"""
    # ベクトル検索
    results = collection.query(query_texts=[user_query], n_results=2)
    context = "\n".join(results['documents'][0]) if results['documents'] else ""

    # Claude用のプロンプト構築
    prompt = f"""以下の参考資料に基づいて、ユーザーの質問に答えてください。

    【参考資料】
    {context}

    【質問】
    {user_query}
    """

    # Claude API呼び出し
    message = claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
