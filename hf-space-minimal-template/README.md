---
title: Chapiko Minimal API
emoji: 🤖
colorFrom: gray
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Chapiko Minimal API

チャピ子の外部サーバ方式で、**最初に接続確認をするための最小API** です。LLMは入っていないので、数十秒でビルドできます。

上の `---` で囲まれた部分は Hugging Face Space の設定です。消さずにそのままアップロードしてください。

## Spaceへ置くファイル

このフォルダの4ファイルをそのままSpaceへアップロードします。

```text
README.md
app.py
requirements.txt
Dockerfile
```

## 確認

Spaceが `Running` になったら、ブラウザで開きます。

```text
https://<ユーザー名>-<Space名>.hf.space/health
```

`{"ok":true,"status":"ready",...}` が出れば成功です。

GitHub Pages の `external-server-llm.html` には、Spaceページの URL（`https://huggingface.co/spaces/<ユーザー名>/<Space名>`）をそのまま貼れば自動で変換されます。

## 任意: 合言葉

Space の Settings → Variables and secrets → **New secret** で `ACCESS_CODE` を設定すると、画面側で同じ合言葉を入れないと `/chat` が 401 になります。LLM版に進む前の確認に使えます。
