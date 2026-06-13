# Chapiko External LLM Server for Hugging Face Spaces

GitHub Pagesを画面だけにして、Hugging Face Space側でLLM推論するためのテンプレートです。

## 構成

```text
GitHub Pages
external-server-llm.html
  ↓ fetch POST /chat
Hugging Face Space
FastAPI + llama.cpp
  ↓
Hugging Face Model Repo
GGUFモデル
```

## Hugging Face Spaceでの作り方

1. Hugging Faceで新しいSpaceを作る
2. SDKは `Docker` を選ぶ
3. このフォルダ内の3ファイルをSpaceへ置く
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
4. SpaceのVariablesに必要なら以下を設定する

```text
MODEL_REPO=TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
MODEL_FILE=tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
N_CTX=2048
N_THREADS=2
MAX_TOKENS=256
TEMPERATURE=0.7
```

5. Spaceが起動したら、次のURLをGitHub Pages側に入れる

```text
https://<your-space-subdomain>.hf.space/chat
```

## 注意

無料CPU Spaceは遅いです。小型GGUFモデルを推奨します。

最初のリクエストでモデルをダウンロード・ロードするため、初回はかなり時間がかかります。

無料ハードウェアは未使用時にスリープします。

## API

### GET /health

```json
{
  "ok": true,
  "model_repo": "...",
  "model_file": "...",
  "loaded": false
}
```

### POST /chat

request:

```json
{
  "message": "こんにちは",
  "system": "あなたはチャピ子です。日本語で短く答えてください。"
}
```

response:

```json
{
  "reply": "こんにちは。チャピ子です。"
}
```
