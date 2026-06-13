# Chapiko Kindle Relay

Kindle のブラウザから「チャピ子」を使うための軽量チャット画面 + Cloudflare Worker 中継アプリです。

## すぐ見るURL

GitHub Pages版の画面はここです。

https://kouheim1979.github.io/chapiko/

このURLでは画面表示を確認できます。実際にチャピ子へ送信するには、画面上の「中継API URL」に Cloudflare Worker の `/api/chat` URLを入れてください。

## できること

- Kindle の古めのブラウザでも開きやすい、白黒・大きめ文字の軽量HTML画面を表示します。
- Kindle側には OpenAI APIキーを置きません。
- Cloudflare Worker が `/api/chat` で OpenAI API に中継します。
- 任意で合言葉 `ACCESS_CODE` を付けられます。
- 会話履歴は Kindle ブラウザの localStorage に保存します。

## 構成

```text
Kindle browser
  ↓
GitHub Pages index.html または Cloudflare Worker HTML page
  ↓
Cloudflare Worker /api/chat
  ↓
OpenAI Responses API
```

## ファイル

```text
README.md                         この説明
index.html                        GitHub Pagesで表示する軽量HTML画面
kindle_chapiko_worker.js           Worker本体。HTML画面もこの中に同梱
wrangler.toml                      Cloudflare Workers設定
package.json                       npm scripts
.github/workflows/pages.yml        GitHub Pages自動デプロイ
.gitignore                         不要ファイル除外
```

## GitHub Pages

`main` ブランチに push すると、`.github/workflows/pages.yml` で GitHub Pages にデプロイします。

公開URL:

```text
https://kouheim1979.github.io/chapiko/
```

Pages版は静的HTMLなので、OpenAI APIキーは置きません。実際に送信するには、Cloudflare Workerをデプロイしてから、画面の「中継API URL」に以下の形で入力します。

```text
https://xxxxx.workers.dev/api/chat
```

## Cloudflare Worker デプロイ手順

### 1. リポジトリを取得

```bash
git clone https://github.com/kouheim1979/chapiko.git
cd chapiko
```

### 2. 依存関係を入れる

```bash
npm install
```

### 3. Cloudflare にログイン

```bash
npx wrangler login
```

### 4. OpenAI APIキーを Secret に保存

```bash
npx wrangler secret put OPENAI_API_KEY
```

ここで OpenAI APIキーを貼り付けます。

### 5. 任意で合言葉を設定

```bash
npx wrangler secret put ACCESS_CODE
```

`ACCESS_CODE` を設定した場合だけ、Kindle画面の「合言葉」欄に同じ文字を入れる必要があります。

### 6. デプロイ

```bash
npm run deploy
```

デプロイ後に表示される `https://xxxxx.workers.dev/` を Kindle のブラウザで開くと、Worker単体でも使えます。

## ローカル確認

```bash
npm run dev
```

通常は `http://localhost:8787/` で確認できます。

## モデル変更

`wrangler.toml` のここを変更します。

```toml
[vars]
OPENAI_MODEL = "gpt-4.1-mini"
```

安く軽く使うなら mini 系、精度重視なら上位モデルにします。

## Kindle向けの使い方

- 短い質問に分けると安定します。
- Kindleでは普通に「送信」ボタンで送ります。
- PCブラウザでは Ctrl+Enter でも送信できます。
- 「短く」「やさしく」ボタンで質問の前に指示を追加できます。
- 「消去」で端末内の会話履歴を消します。

## 注意

- `chatgpt.com` を直接埋め込むアプリではありません。Kindleの古いブラウザ、ログイン、CSP、重いJavaScriptの問題を避けるため、OpenAI APIを使う中継方式にしています。
- OpenAI API利用料はAPIアカウント側に発生します。
- APIキーは `wrangler.toml` やHTMLに書かないでください。必ず `wrangler secret put OPENAI_API_KEY` で設定してください。
