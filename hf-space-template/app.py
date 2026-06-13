import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_cpp import Llama

MODEL_REPO = os.getenv("MODEL_REPO", "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF")
MODEL_FILE = os.getenv("MODEL_FILE", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
N_CTX = int(os.getenv("N_CTX", "2048"))
N_THREADS = int(os.getenv("N_THREADS", "2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "256"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

app = FastAPI(title="Chapiko External LLM Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_llm: Optional[Llama] = None


class ChatRequest(BaseModel):
    message: str
    system: str = "あなたはチャピ子です。日本語で、結論から、短く答えてください。"


def get_llm() -> Llama:
    global _llm
    if _llm is None:
        _llm = Llama.from_pretrained(
            repo_id=MODEL_REPO,
            filename=MODEL_FILE,
            n_ctx=N_CTX,
            n_threads=N_THREADS,
            verbose=False,
        )
    return _llm


@app.get("/health")
def health():
    return {
        "ok": True,
        "model_repo": MODEL_REPO,
        "model_file": MODEL_FILE,
        "loaded": _llm is not None,
    }


@app.post("/chat")
def chat(req: ChatRequest):
    llm = get_llm()
    result = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": req.system},
            {"role": "user", "content": req.message},
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    reply = result["choices"][0]["message"]["content"]
    return {"reply": reply}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
