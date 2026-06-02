from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # フェーズ2時点ではモック（オウム返し）を返す
    return {"answer": f"受信しました: {request.message}"}
