#src/backend/app/rag.py
import os
import google.generativeai as genai
from chromadb import HttpClient
from pypdf import PdfReader
from pypdf.errors import PdfReadError

# Gemini APIキーの設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ChromaDBクライアントの初期化
chroma_client = HttpClient(
    host=os.environ.get("CHROMA_HOST", "vectordb"),
    port=int(os.environ.get("CHROMA_PORT", 8000))
)
collection = chroma_client.get_or_create_collection(name="pdf_documents")

# Gemini生成モデル（回答生成用）
generation_model = genai.GenerativeModel("gemini-1.5-flash")

# 埋め込みモデル名（text-embedding-004）
EMBEDDING_MODEL = "models/text-embedding-004"

def get_embedding(text: str, task_type: str = "retrieval_document") -> list:
    """Gemini text-embedding-004でテキストをベクトル化"""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=str(text).strip()
    )
    return result["embedding"]


def extract_text_from_pdf(pdf_path: str) -> str:
    """PDFからテキストを抽出（テキストPDF→OCRの順で試みる）"""
    # まずPyPDFでテキスト抽出を試みる
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
        if full_text.strip():
            return full_text
    except PdfReadError:
        pass

    # テキストが空の場合はOCRで抽出
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


def extract_and_store_pdf(pdf_path: str, document_id: str) -> int:
    """1. PDFからテキストを抽出してChromaへ格納"""
    full_text = extract_text_from_pdf(pdf_path)

    if not full_text.strip():
        raise ValueError("PDFからテキストを抽出できませんでした")

    # テキストをチャンク分割（chunk_size=500, overlap=100）
    chunks = [str(full_text[i:i+500]) for i in range(0, len(full_text), 400)]
    chunks = [c for c in chunks if c.strip()]  # 空チャンクを除外

    if not chunks:
        return 0

    # チャンクごとにGemini text-embedding-004でベクトル化
    embeddings = []
    for chunk in chunks:
#        embedding = get_embedding(chunk, task_type="retrieval_document")
        embedding = get_embedding(chunk)
        embeddings.append(embedding)

    # ChromaDBに登録
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"{document_id}_{i}" for i in range(len(chunks))]
    )
    return len(chunks)


def answer_with_rag(user_query: str) -> str:
    """2. ユーザーの質問に対してRAGで回答生成"""
    # Gemini text-embedding-004でクエリをベクトル化して検索
#    query_embedding = get_embedding(user_query, task_type="retrieval_query")
    query_embedding = get_embedding(user_query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    context = "\n".join(results['documents'][0]) if results['documents'] else ""

    if not context:
        return "関連するドキュメントが見つかりませんでした。先にPDFをインデックス化してください。"

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
