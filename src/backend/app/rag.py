# src/backend/app/rag.py
import os
from typing import Optional
import re
import time

# import google.generativeai as genai
import google.genai as genai  # ← これが正しい
import chromadb
from pypdf import PdfReader
from pypdf.errors import PdfReadError

# -----------------------------
# Gemini API 初期化（v1 エンドポイント強制）
# -----------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# -----------------------------
# モデル名（v1 形式）
# -----------------------------
EMBEDDING_MODEL = "models/gemini-embedding-2"
GENERATION_MODEL = "models/gemini-2.5-flash-lite"


def debug_list_models():
    print("---- 利用可能なモデル一覧 ----")
    models = client.models.list()
    for m in models:
        actions = getattr(m, "supported_actions", None)
        print(m.name, "→ actions:", actions)


client = genai.Client(api_key=GEMINI_API_KEY)

# モデル一覧を表示（起動時に一度だけ）
debug_list_models()
# -----------------------------
# ChromaDB 初期化
# -----------------------------
chroma_client = chromadb.HttpClient(
    host=os.getenv("CHROMA_HOST", "vectordb"), port=int(os.getenv("CHROMA_PORT", 8000))
)
collection = chroma_client.get_or_create_collection(name="pdf_documents")


# -----------------------------
# 文単位チャンク化ロジック
# -----------------------------
def split_into_sentences(text: str):
    sentences = re.split(r"(?<=[。！？])\s*", text)
    return [s for s in sentences if s.strip()]


def chunk_sentences(sentences, max_chars=500):
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) > max_chars:
            chunks.append(current)
            current = s
        else:
            current += s
    if current:
        chunks.append(current)
    return chunks


# -----------------------------
# 埋め込み生成（リトライあり）
# -----------------------------
def get_embedding(text: str, retry: int = 3) -> list:
    t = str(text).strip()
    for attempt in range(retry):
        try:
            result = client.models.embed_content(model=EMBEDDING_MODEL, contents=t)
            embeddings = result.embeddings
            if embeddings is None:
                raise ValueError("embeddingsがNoneです")
            return list(embeddings[0].values)

        except Exception as e:
            print(f"ベクトル化エラー（試行{attempt + 1}/{retry}）: {e}")
            if attempt < retry - 1:
                time.sleep(2**attempt)
            else:
                raise


# -----------------------------
# PDFテキスト抽出
# -----------------------------
def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
        if full_text.strip():
            return full_text
    except PdfReadError:
        pass

    print(f"テキスト抽出できないためOCRを使用: {pdf_path}")
    try:
        import pytesseract
        from pdf2image import convert_from_path

        images = convert_from_path(pdf_path, dpi=200)
        ocr_text = ""
        for image in images:
            ocr_text += pytesseract.image_to_string(image, lang="jpn+eng") + "\n"
        return ocr_text
    except Exception as e:
        raise RuntimeError(f"OCRに失敗しました: {str(e)}")


# -----------------------------
# PDF → ChromaDB 登録
# -----------------------------
def extract_and_store_pdf(pdf_path: str, document_id: str) -> int:
    full_text = extract_text_from_pdf(pdf_path)

    if not full_text.strip():
        raise ValueError("PDFからテキストを抽出できませんでした")

    sentences = split_into_sentences(full_text)
    print(f"full_text={full_text[:20]}")
    print(f"sentences number={len(sentences)}")
    chunks = chunk_sentences(sentences)

    if not chunks:
        return 0

    print(f"チャンク数: {len(chunks)}")

    embeddings = []
    for i, chunk in enumerate(chunks):
        print(f"ベクトル化中: {i + 1}/{len(chunks)}")
        embedding = get_embedding(chunk)
        embeddings.append(embedding)
        time.sleep(0.1)

    import numpy as np

    embeddings_array = [np.array(e, dtype=np.float32) for e in embeddings]
    collection.add(
        documents=chunks,
        embeddings=embeddings_array,
        ids=[f"{document_id}_{i}" for i in range(len(chunks))],
        metadatas=[
            {"source": document_id, "chunk": i, "registered_at": str(time.time())}
            for i in range(len(chunks))
        ],
    )

    return len(chunks)


# -----------------------------
# RAG回答生成
# -----------------------------
def answer_with_rag(user_query: str, model: Optional[str] = None) -> str:
    use_model = model or GENERATION_MODEL
    query_embedding = get_embedding(user_query)

    import numpy as np

    results = collection.query(
        query_embeddings=[np.array(query_embedding, dtype=np.float32)], n_results=5
    )

    context = "\n".join(results["documents"][0]) if results["documents"] else ""

    if not context:
        return "関連するドキュメントが見つかりませんでした。先にPDFをインデックス化してください。"

    prompt = f"""
あなたは与えられた参考資料に基づいて正確に回答するアシスタントです。
参考資料にない内容は推測せず「資料に記載がありません」と答えてください。

【参考資料】
{context}

【質問】
{user_query}

【回答】
"""

    response = client.models.generate_content(model=use_model, contents=prompt)
    return response.text
