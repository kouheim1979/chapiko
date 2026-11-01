---
title: Chapiko LLM
emoji: 🤖
colorFrom: gray
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Chapiko External LLM Server for Hugging Face Spaces

GitHub Pagesを画面だけにして、Hugging Face Space（無料CPU）側でLLM推論するためのテンプレートです。

上の `---` で囲まれた部分は Hugging Face Space の設定です。消さずにそのままアップロードしてください。

## 構成

```text
GitHub Pages
external-server-llm.html（PC / スマホ / Kindle）
  ↓ POST /chat
Hugging Face Space（Docker / 無料CPU 2コア 16GB）
FastAPI + transformers（CPU版torch）
  ↓ 初回起動時にダウンロード
Hugging Face Model
既定: Qwen/Qwen2.5-0.5B-Instruct（日本語OK・軽量）
```

## Hugging Face Spaceでの作り方

1. Hugging Faceで新しいSpaceを作る
2. SDKは `Docker`（テンプレートは `Blank`）、ハードウェアは `CPU basic (free)`
3. このフォルダ内の4ファイルをSpaceへアップロードする
   - `README.md`
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
4. ビルド完了後（初回5〜10分）、Spaceが `Running` になる
5. モデルは起動後に裏でダウンロード・読み込みします（1〜3分）。
   `https://<ユーザー名>-<Space名>.hf.space/health` が `"status":"ready"` になれば準備完了
6. GitHub Pages の `external-server-llm.html` に、SpaceページのURLを貼る

## 設定（任意）

Space の Settings → Variables and secrets で変更できます。何も設定しなくても動きます。

```text
MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct   使うモデル
MAX_NEW_TOKENS=256                    回答の最大トークン数
TEMPERATURE=0.7                       0にすると毎回同じ答え
TOP_P=0.9
N_THREADS=2                           無料CPUは2コア
MAX_HISTORY=6                         会話履歴として使う直近メッセージ数
MAX_INPUT_CHARS=2000                  1メッセージの最大文字数
```

合言葉を付ける場合は **Secret** で設定します（公開Spaceは誰でも叩けるため推奨）。

```text
ACCESS_CODE=好きな合言葉
```

### モデルの目安（無料CPU 2コア）

```text
Qwen/Qwen2.5-0.5B-Instruct   既定。速い。日本語OK
Qwen/Qwen2.5-1.5B-Instruct   賢くなるが2〜3倍遅い
HuggingFaceTB/SmolLM2-360M-Instruct  超軽量。日本語は弱い
```

3B以上は無料CPUでは実用的な速さになりません。

## 注意

- 無料CPU Spaceは遅いです。0.5Bモデルで1回答に10〜40秒ほどかかります。
- 無料Spaceは48時間使わないとスリープします。スリープ明けは、画面の「起こす」ボタンで `/health` が `ready` になるまで待ってから質問してください。
- 同時に来た質問は1件ずつ順番に処理します。

## API

### GET /health

```json
{
  "ok": true,
  "status": "ready",
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "loaded": true,
  "error": "",
  "access_code_required": false
}
```

`status` は `loading`（読み込み中）/ `ready`（使える）/ `error`（失敗。`error` に原因）のどれかです。

### POST /chat

request:

```json
{
  "message": "こんにちは",
  "system": "あなたはチャピ子です。日本語で短く答えてください。",
  "history": [
    {"role": "user", "content": "前の質問"},
    {"role": "assistant", "content": "前の答え"}
  ],
  "code": "合言葉（ACCESS_CODEを設定した場合だけ）"
}
```

response:

```json
{
  "reply": "こんにちは。チャピ子です。",
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "elapsed_sec": 12.3
}
```

エラー時は `{"error": "..."}` を返します（401 合言葉違い / 503 モデル読み込み中 / 500 失敗）。
