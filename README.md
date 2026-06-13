# チャピ子 Kindle

Kindleで見やすい入口ページです。

## 開くURL

```text
https://kouheim1979.github.io/chapiko/
```

## 追加したもの

### 簡易LLM チャピ子ミニ

```text
https://kouheim1979.github.io/chapiko/simple-llm.html
```

これは本物の大規模LLMではありません。GitHub Pagesだけで動く、API不要・無料の簡易チャットです。

できること:

- キーワードに近い内蔵知識を返す
- 端末内の localStorage に「学習メモ」を保存する
- Kindle向けに白黒・大文字・軽量HTMLで表示する
- OpenAI APIキーなしで動く

できないこと:

- ChatGPTと同じ精度で考える
- 最新情報を自動で調べる
- 別端末に学習内容を同期する
- 本物のLLMのように自然に長文生成する

### オンライン表示中継

VDO.Ninja の `push` と `view` のリンクを作ります。

- ローカルサーバーなし
- OpenAI APIキーなし
- Cloudflare Workerなし
- 送信側は `push` リンク
- 表示側は `view` リンク

ただし、Kindle側ブラウザがWebRTCに対応していない場合は映らないことがあります。

## ファイル

```text
index.html                         入口ページ
simple-llm.html                    APIなし簡易チャット
.github/workflows/pages.yml        GitHub Pages自動デプロイ
README.md                          この説明
```
