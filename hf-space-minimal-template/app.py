"""Chapiko Minimal API (Hugging Face Space 接続確認用)

LLMは入っていません。GitHub Pages の画面からの接続・CORS・合言葉が
正しく通るかを確認するためのサーバです。応答は LLM 版と同じ形式です。

  GET  /health  -> {ok, status:"ready", ...}
  POST /chat    {message, system?, history?, code?} -> {reply, model, elapsed_sec}

ACCESS_CODE を Space の Secret に設定すると、合言葉の確認もできます。
"""

import os
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

ACCESS_CODE = os.getenv("ACCESS_CODE", "")

app = FastAPI(title="Chapiko Minimal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Turn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    system: str = "あなたはチャピ子です。"
    history: List[Turn] = []
    code: Optional[str] = None


@app.get("/")
def root():
    return {
        "ok": True,
        "name": "Chapiko Minimal API",
        "status": "ready",
        "endpoints": ["/health", "/chat", "/docs"],
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "status": "ready",
        "model": "minimal-echo",
        "loaded": True,
        "access_code_required": bool(ACCESS_CODE),
        "message": "Chapiko minimal server is running.",
    }


@app.post("/chat")
def chat(req: ChatRequest):
    if ACCESS_CODE and (req.code or "") != ACCESS_CODE:
        return JSONResponse(status_code=401, content={"error": "合言葉が違います"})
    return {
        "reply": (
            "チャピ子最小APIです。外部サーバ接続は成功しています。"
            "質問は「" + req.message + "」です。"
            "（会話履歴 " + str(len(req.history)) + " 件を受信）"
        ),
        "model": "minimal-echo",
        "elapsed_sec": 0,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
