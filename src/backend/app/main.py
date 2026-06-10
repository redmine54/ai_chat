from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
import os
import glob
from pathlib import Path

# /app/app/main.py → /app/app → /app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


# キャッシュ無効化ミドルウェア
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response


app = FastAPI(
    docs_url=None,
    redoc_url="/swagger/redoc",
    openapi_url="/swagger/openapi.json"
)

@app.get("/swagger/docs", include_in_schema=False)
async def custom_swagger_ui():
    from fastapi.responses import HTMLResponse
    return HTMLResponse("""<!DOCTYPE html>
<html>
<head>
  <title>Swagger UI</title>
  <meta charset="utf-8"/>
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
</head>
<body>
  <nav style="background:#2c2c2c;padding:10px 20px;display:flex;gap:12px;align-items:center;">
    <span style="color:#aaa;font-size:13px;margin-right:8px;">🔗 メニュー:</span>
    <a href="/api/chat/ui" style="color:#fff;background:#4a90d9;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:13px;">💬 チャット</a>
    <a href="/api/indexer" style="color:#fff;background:#4a90d9;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:13px;">📄 PDFインデクサー</a>
    <a href="/api/specs" style="color:#fff;background:#4a90d9;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:13px;">📚 ドキュメント</a>
    <a href="/swagger/docs" style="color:#fff;background:#4a90d9;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:13px;">🔧 API</a>
  </nav>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: "/swagger/openapi.json",
      dom_id: '#swagger-ui',
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout"
    })
  </script>
</body>
</html>""")

app.add_middleware(NoCacheMiddleware)


class ChatRequest(BaseModel):
    message: str
    model: str = "models/gemini-2.5-flash"


class IndexRequest(BaseModel):
    filename: str  # data/配下のファイル名
    force: bool = False  # 強制再登録フラグ


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """RAG+Geminiで回答生成"""
    from app.rag import answer_with_rag
    try:
        answer = answer_with_rag(request.message, model=request.model)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回答生成に失敗しました: {str(e)}")


@app.get("/api/pdf/list")
async def list_pdfs():
    """data/配下のPDFファイル一覧を返す"""
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    filenames = [os.path.basename(f) for f in pdf_files]
    return {"files": filenames}


@app.post("/api/pdf/index")
async def index_pdf(request: IndexRequest):
    """指定したPDFをインデックス化してChromaDBに登録する"""
    from app.rag import extract_and_store_pdf

    pdf_path = os.path.join(DATA_DIR, request.filename)

    # ファイル存在チェック
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"ファイルが見つかりません: {request.filename}")

    # 拡張子チェック
    if not request.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDFファイルのみ対応しています")

    try:
        document_id = Path(request.filename).stem
        chunk_count = extract_and_store_pdf(pdf_path, document_id)
        return {
            "status": "success",
            "filename": request.filename,
            "document_id": document_id,
            "chunks": chunk_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"インデックス化に失敗しました: {str(e)}")


# HTMLテンプレートディレクトリ
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# favicon

class DeleteRequest(BaseModel):
    document_id: str


@app.get("/api/pdf/status")
async def pdf_status(filename: str):
    """PDFの登録状況・ページ数・チャンク数を返す"""
    from app.rag import collection
    from pypdf import PdfReader
    import os

    pdf_path = os.path.join(DATA_DIR, filename)
    document_id = Path(filename).stem

    # PDFのページ数・更新日時を取得
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"ファイルが見つかりません: {filename}")

    try:
        reader = PdfReader(pdf_path)
        page_count = len(reader.pages)
    except Exception:
        page_count = None

    pdf_mtime = os.path.getmtime(pdf_path)

    # ChromaDBの登録状況を確認
    existing = collection.get(where={"source": document_id})
    chunk_count = len(existing["ids"])

    if chunk_count == 0:
        status = "unregistered"
        registered_at = None
    else:
        # メタデータから登録日時を取得
        registered_at = None
        for meta in existing["metadatas"]:
            if meta.get("registered_at"):
                registered_at = float(meta["registered_at"])
                break

        if registered_at and pdf_mtime > registered_at:
            status = "outdated"
        else:
            status = "registered"

    return {
        "filename": filename,
        "document_id": document_id,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "status": status,
        "pdf_mtime": pdf_mtime,
        "registered_at": registered_at,
    }


@app.delete("/api/pdf/delete")
async def delete_pdf(request: DeleteRequest):
    """ChromaDBから指定ドキュメントのデータを削除する"""
    from app.rag import collection

    existing = collection.get(where={"source": request.document_id})
    if not existing["ids"]:
        raise HTTPException(status_code=404, detail=f"登録データが見つかりません: {request.document_id}")

    collection.delete(ids=existing["ids"])
    return {
        "status": "success",
        "document_id": request.document_id,
        "deleted_chunks": len(existing["ids"])
    }

@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(BASE_DIR, "static", "favicon.ico"))

# docsディレクトリを静的ファイルとして公開
app.mount("/api/docs", StaticFiles(directory=os.path.join(BASE_DIR, "docs")), name="docs")

# ルート直下のREADME.md用
if os.path.exists(os.path.join(BASE_DIR, "README.md")):
    app.mount("/api/root_meta", StaticFiles(directory=BASE_DIR), name="root_meta")

# チャット画面（メイン）
@app.get("/", response_class=HTMLResponse)
@app.get("/api/chat/ui", response_class=HTMLResponse)
async def read_chat(request: Request):
    return templates.TemplateResponse(request, "chat.html")

# ドキュメントビューア
@app.get("/api/specs", response_class=HTMLResponse)
async def read_specs(request: Request):
    return templates.TemplateResponse(request, "specs.html")

# PDFインデクサー画面
@app.get("/api/indexer", response_class=HTMLResponse)
async def read_indexer(request: Request):
    return templates.TemplateResponse(request, "indexer.html")
