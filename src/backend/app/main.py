from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

# /app/app/main.py → /app/app → /app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # フェーズ2時点ではモック（オウム返し）を返す
    return {"answer": f"受信しました: {request.message}"}

# 1. HTMLテンプレートを置くディレクトリを指定
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# /app/app/static/favicon.ico を作る。
#app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(BASE_DIR, "static", "favicon.ico"))

# 2. docsディレクトリを静的ファイルとして公開
app.mount("/api/docs", StaticFiles(directory=os.path.join(BASE_DIR, "docs")), name="docs")

# 3. ルート直下のREADME.md用
if os.path.exists(os.path.join(BASE_DIR, "README.md")):
    app.mount("/api/root_meta", StaticFiles(directory=BASE_DIR), name="root_meta")

# 4. http://localhost:8000/specs にアクセスしたときの処理
@app.get("/api/specs", response_class=HTMLResponse)
async def read_specs(request: Request):
    print(f"BASE_DIR : {BASE_DIR}")
    print(f"request : {request}")

    return templates.TemplateResponse(request, "specs.html")

#    return templates.TemplateResponse("specs.html", {"request": request})
