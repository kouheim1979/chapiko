"""Chapiko External LLM Server (Hugging Face Space / CPU / transformers)

GitHub Pages の external-server-llm.html から呼ばれる API サーバです。

  GET  /health  起動状態とモデル読み込み状態
  POST /chat    {message, system?, history?, code?} -> {reply, model, elapsed_sec}

モデルは起動直後にバックグラウンドで読み込みます。読み込み中の /chat は
503 を返すので、画面側は「起こす」ボタンで /health を待ってから質問します。

Space の Variables / Secrets で調整できます（どれも省略可）:

  MODEL_ID        既定 Qwen/Qwen2.5-0.5B-Instruct
  MAX_NEW_TOKENS  既定 256
  TEMPERATURE     既定 0.7 (0 で毎回同じ答え)
  TOP_P           既定 0.9
  N_THREADS       既定 2 (無料CPU Spaceは2コア)
  MAX_HISTORY     既定 6 (会話履歴として使う直近メッセージ数)
  MAX_INPUT_CHARS 既定 2000
  ACCESS_CODE     Secret推奨。設定すると合言葉が合わない /chat を拒否
"""

import os
import threading
import time
import traceback
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "256"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))
N_THREADS = int(os.getenv("N_THREADS", "2"))
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "6"))
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "2000"))
ACCESS_CODE = os.getenv("ACCESS_CODE", "")

DEFAULT_SYSTEM = "あなたはチャピ子です。日本語で、結論から、短く答えてください。"
RETRY_INTERVAL_SEC = 60

_state = {
    "status": "starting",  # starting -> loading -> ready / error
    "error": "",
    "load_sec": None,
    "last_try": 0.0,
}
_model = None
_tokenizer = None
_load_lock = threading.Lock()
_generate_lock = threading.Lock()
_started_at = time.time()


class Turn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    system: str = DEFAULT_SYSTEM
    history: List[Turn] = []
    code: Optional[str] = None


def load_model():
    """モデルとトークナイザを読み込む。2回目以降は何もしない。"""
    global _model, _tokenizer
    with _load_lock:
        if _model is not None:
            return
        _state["status"] = "loading"
        _state["error"] = ""
        _state["last_try"] = time.time()
        started = time.time()
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            torch.set_num_threads(max(1, N_THREADS))
            tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
            model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
            # CPUでは float32 が一番確実。transformers 4/5 どちらでも動くよう読み込み後に変換する。
            model = model.to(torch.float32)
            model.eval()
            _tokenizer = tokenizer
            _model = model
            _state["status"] = "ready"
            _state["load_sec"] = round(time.time() - started, 1)
            print("[chapiko] model ready: %s (%.1fs)" % (MODEL_ID, time.time() - started), flush=True)
        except Exception as e:  # noqa: BLE001 - 画面に原因を出すため全部拾う
            _state["status"] = "error"
            _state["error"] = "%s: %s" % (type(e).__name__, e)
            traceback.print_exc()


def start_background_load():
    threading.Thread(target=load_model, daemon=True).start()


@asynccontextmanager
async def lifespan(_app):
    # Spaceが「Running」になるのを待たせないよう、モデルは裏で読み込む
    start_background_load()
    yield


app = FastAPI(title="Chapiko External LLM Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error(status: int, message: str):
    return JSONResponse(status_code=status, content={"error": message})


def build_messages(req: ChatRequest):
    system = (req.system or DEFAULT_SYSTEM).strip()[:MAX_INPUT_CHARS]
    messages = [{"role": "system", "content": system}]
    history = req.history[-MAX_HISTORY:] if MAX_HISTORY > 0 else []
    for turn in history:
        role = "assistant" if turn.role in ("assistant", "bot") else "user"
        content = (turn.content or "").strip()[:MAX_INPUT_CHARS]
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": req.message.strip()[:MAX_INPUT_CHARS]})
    return messages


def render_prompt(messages):
    """チャットテンプレートで文字列化する。system非対応モデル(Gemma等)は先頭のuserに混ぜる。"""
    try:
        return _tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    except Exception:
        system = messages[0]["content"]
        rest = [dict(m) for m in messages[1:]]
        for m in rest:
            if m["role"] == "user":
                m["content"] = system + "\n\n" + m["content"]
                break
        return _tokenizer.apply_chat_template(rest, tokenize=False, add_generation_prompt=True)


def generate(messages) -> str:
    import torch

    prompt = render_prompt(messages)
    inputs = _tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    kwargs = {
        "max_new_tokens": MAX_NEW_TOKENS,
        "repetition_penalty": 1.1,
        "pad_token_id": _tokenizer.pad_token_id if _tokenizer.pad_token_id is not None else _tokenizer.eos_token_id,
    }
    if TEMPERATURE > 0:
        kwargs.update({"do_sample": True, "temperature": TEMPERATURE, "top_p": TOP_P})
    else:
        kwargs.update({"do_sample": False})
    with torch.inference_mode():
        output = _model.generate(**inputs, **kwargs)
    new_tokens = output[0][inputs["input_ids"].shape[-1]:]
    return _tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


@app.get("/")
def root():
    return {
        "ok": True,
        "name": "Chapiko External LLM Server",
        "status": _state["status"],
        "model": MODEL_ID,
        "endpoints": ["/health", "/chat", "/docs"],
    }


@app.get("/health")
def health():
    if (
        _state["status"] == "error"
        and not _load_lock.locked()
        and time.time() - _state["last_try"] > RETRY_INTERVAL_SEC
    ):
        # 失敗後に /health を叩いたら読み込みをやり直す（一時的な通信エラー対策）
        _state["last_try"] = time.time()
        start_background_load()
    return {
        "ok": _state["status"] == "ready",
        "status": _state["status"],
        "model": MODEL_ID,
        "loaded": _model is not None,
        "error": _state["error"],
        "load_sec": _state["load_sec"],
        "uptime_sec": round(time.time() - _started_at, 1),
        "access_code_required": bool(ACCESS_CODE),
        "max_new_tokens": MAX_NEW_TOKENS,
    }


@app.post("/chat")
def chat(req: ChatRequest):
    if ACCESS_CODE and (req.code or "") != ACCESS_CODE:
        return error(401, "合言葉が違います")
    if not req.message.strip():
        return error(400, "質問が空です")
    if len(req.message) > MAX_INPUT_CHARS:
        return error(400, "質問が長すぎます。%d文字以内に分けてください。" % MAX_INPUT_CHARS)
    if _model is None:
        if _state["status"] == "error":
            return error(500, "モデル読み込みに失敗しています: " + _state["error"])
        return error(503, "モデル読み込み中です。1〜3分ほど待ってからもう一度送ってください。")

    started = time.time()
    try:
        # 無料CPUは2コアなので同時生成はさせず1件ずつ処理する
        with _generate_lock:
            reply = generate(build_messages(req))
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()
        return error(500, "生成エラー: %s: %s" % (type(e).__name__, e))
    return {
        "reply": reply or "(返答が空でした)",
        "model": MODEL_ID,
        "elapsed_sec": round(time.time() - started, 1),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
