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
import asyncio
from fastapi.responses import StreamingResponse
import urllib.request
import json as json_module


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
    docs_url=None, redoc_url="/swagger/redoc", openapi_url="/swagger/openapi.json"
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
        raise HTTPException(
            status_code=404, detail=f"ファイルが見つかりません: {request.filename}"
        )

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
            "chunks": chunk_count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"インデックス化に失敗しました: {str(e)}"
        )


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
        raise HTTPException(
            status_code=404, detail=f"ファイルが見つかりません: {filename}"
        )

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
        metadatas = existing.get("metadatas") or []
        for meta in metadatas:
            val = meta.get("registered_at") if meta else None
            if val is not None:
                try:
                    registered_at = float(str(val))
                except (ValueError, TypeError):
                    pass
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
        raise HTTPException(
            status_code=404, detail=f"登録データが見つかりません: {request.document_id}"
        )

    collection.delete(ids=existing["ids"])
    return {
        "status": "success",
        "document_id": request.document_id,
        "deleted_chunks": len(existing["ids"]),
    }


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(BASE_DIR, "static", "favicon.ico"))


# docsディレクトリを静的ファイルとして公開
app.mount(
    "/api/docs", StaticFiles(directory=os.path.join(BASE_DIR, "docs")), name="docs"
)

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


# 実行許可スクリプト一覧（セキュリティのため明示的に許可）
ALLOWED_SCRIPTS = [
    "check_chroma.sh",
    "check_models.sh",
    "switch_gemini_model.sh",
    "switch_to_compose.sh",
    "rebuild_compose.sh",
    "switch_to_minikube.sh",
    "minikube_start.sh",
    "minikube_start_https.sh",
    "minikube_build.sh",
    "minikube_build_https.sh",
    "rebuild_minikube.sh",
    "switch_to_http.sh",
    "switch_to_https.sh",
    "外部公開_compose.sh",
]


class ShRequest(BaseModel):
    script: str


@app.post("/api/sh/run")
async def run_script(request: ShRequest):
    """シェルスクリプトを実行してログをストリーミング返却する"""
    if request.script not in ALLOWED_SCRIPTS:
        raise HTTPException(
            status_code=403, detail=f"実行が許可されていません: {request.script}"
        )

    script_path = os.path.join(BASE_DIR, "..", request.script)
    script_path = os.path.abspath(script_path)

    if not os.path.exists(script_path):
        raise HTTPException(
            status_code=404, detail=f"スクリプトが見つかりません: {request.script}"
        )

    async def stream_output():
        proc = await asyncio.create_subprocess_exec(
            "bash",
            script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.dirname(script_path),
        )
        async for line in proc.stdout:
            yield line.decode("utf-8", errors="replace")
        await proc.wait()
        yield f"\n[終了コード: {proc.returncode}]\n"

    return StreamingResponse(stream_output(), media_type="text/plain")


# ユーティリティ画面
@app.get("/api/utilities", response_class=HTMLResponse)
async def read_utilities(request: Request):
    return templates.TemplateResponse(request, "utilities.html")


GITHUB_REPO = "redmine54/ai_chat"


@app.get("/api/ci/runs")
async def get_ci_runs():
    """GitHub ActionsのCI実行結果一覧を取得する"""
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs?per_page=10"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "aichat-ci-viewer",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json_module.loads(res.read())
        runs = []
        for r in data.get("workflow_runs", []):
            runs.append(
                {
                    "id": r["id"],
                    "name": r["name"],
                    "branch": r["head_branch"],
                    "commit": r["head_sha"][:7],
                    "commit_msg": r["head_commit"]["message"].split("\n")[0]
                    if r.get("head_commit")
                    else "",
                    "status": r["status"],
                    "conclusion": r["conclusion"],
                    "created_at": r["created_at"],
                    "html_url": r["html_url"],
                }
            )
        return {"runs": runs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub API取得失敗: {str(e)}")


@app.get("/api/ci/runs/{run_id}/jobs")
async def get_ci_jobs(run_id: int):
    """指定したCI実行のジョブ・ステップ詳細を取得する"""
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}/jobs"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "aichat-ci-viewer",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json_module.loads(res.read())
        jobs = []
        for j in data.get("jobs", []):
            steps = []
            for s in j.get("steps", []):
                steps.append(
                    {
                        "name": s["name"],
                        "status": s["status"],
                        "conclusion": s["conclusion"],
                        "number": s["number"],
                        "started_at": s.get("started_at"),
                        "completed_at": s.get("completed_at"),
                    }
                )
            jobs.append(
                {
                    "id": j["id"],
                    "name": j["name"],
                    "status": j["status"],
                    "conclusion": j["conclusion"],
                    "started_at": j.get("started_at"),
                    "completed_at": j.get("completed_at"),
                    "html_url": j["html_url"],
                    "steps": steps,
                }
            )
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub API取得失敗: {str(e)}")


@app.get("/api/ci/runs/{run_id}/logs/{job_id}")
async def get_ci_logs(run_id: int, job_id: int):
    """指定したジョブのログを取得する"""
    import urllib.parse

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise HTTPException(status_code=401, detail="GITHUB_TOKENが設定されていません")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/jobs/{job_id}/logs"

    # リダイレクトを手動で追いかける
    try:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "aichat-ci-viewer",
        }

        # urllib でリダイレクトを追跡するカスタムハンドラー
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                # リダイレクト先にはAuthorizationヘッダーを付けない（Azure Blob Storage）
                return urllib.request.Request(
                    newurl, headers={"User-Agent": "aichat-ci-viewer"}
                )

        opener = urllib.request.build_opener(NoRedirectHandler())
        req = urllib.request.Request(url, headers=headers)
        with opener.open(req, timeout=15) as res:
            logs = res.read().decode("utf-8", errors="replace")
        return {"logs": logs[:50000]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ログ取得失敗: {str(e)}")


# CI結果画面
@app.get("/api/ci", response_class=HTMLResponse)
async def read_ci(request: Request):
    return templates.TemplateResponse(request, "ci.html")


# PDFインデクサー画面
@app.get("/api/indexer", response_class=HTMLResponse)
async def read_indexer(request: Request):
    return templates.TemplateResponse(request, "indexer.html")
