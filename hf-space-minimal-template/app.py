import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Chapiko Minimal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    system: str = "あなたはチャピ子です。"


@app.get("/")
def root():
    return {
        "ok": True,
        "name": "Chapiko Minimal API",
        "status": "running",
        "endpoints": ["/health", "/chat", "/docs"],
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "message": "Chapiko minimal server is running.",
    }


@app.post("/chat")
def chat(req: ChatRequest):
    return {
        "reply": "チャピ子最小APIです。外部サーバ接続は成功しています。質問は「" + req.message + "」です。"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
