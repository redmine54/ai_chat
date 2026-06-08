from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
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
    docs_url="/swagger/docs",
    redoc_url="/swagger/redoc",
    openapi_url="/swagger/openapi.json"
)

app.add_middleware(NoCacheMiddleware)


class ChatRequest(BaseModel):
    message: str


class IndexRequest(BaseModel):
    filename: str  # data/配下のファイル名


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """RAG+Geminiで回答生成"""
    from app.rag import answer_with_rag
    try:
        answer = answer_with_rag(request.message)
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


# 1. HTMLテンプレートを置くディレクトリを指定
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# favicon
@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(BASE_DIR, "static", "favicon.ico"))

# 2. docsディレクトリを静的ファイルとして公開
app.mount("/api/docs", StaticFiles(directory=os.path.join(BASE_DIR, "docs")), name="docs")

# 3. ルート直下のREADME.md用
if os.path.exists(os.path.join(BASE_DIR, "README.md")):
    app.mount("/api/root_meta", StaticFiles(directory=BASE_DIR), name="root_meta")

# 4. ドキュメントビューア
@app.get("/api/specs", response_class=HTMLResponse)
async def read_specs(request: Request):
    print(f"BASE_DIR : {BASE_DIR}")
    print(f"request : {request}")
    return templates.TemplateResponse(request, "specs.html")

# 5. PDFインデクサー画面
@app.get("/api/indexer", response_class=HTMLResponse)
async def read_indexer(request: Request):
    return templates.TemplateResponse(request, "indexer.html")
