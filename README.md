# チャピ子 表示中継

Kindle のブラウザから ChatGPT / チャピ子を開くための、軽い中継ページです。

## 開くURL

```text
https://kouheim1979.github.io/chapiko/
```

## これは何？

GitHub Pagesに置いた、ただの軽量HTMLです。

- APIキーは使いません。
- OpenAI APIも使いません。
- Cloudflare Workerも必須ではありません。
- Kindleでブックマークしやすい入口ページです。
- 大きいボタンで `https://chatgpt.com/` を開きます。
- 可能ならページ内の iframe に ChatGPT 画面を表示します。

## 注意

ChatGPT側のセキュリティ設定によって、iframe内に画面が出ないことがあります。その場合は、ページ上部の「チャピ子を開く」ボタンから同じタブで開いてください。

## ファイル

```text
index.html                         表示中継ページ
.github/workflows/pages.yml        GitHub Pages自動デプロイ
README.md                          この説明
```

以前入れた Cloudflare Worker 関連ファイルは残していますが、今回の「表示中継だけ」なら使わなくて大丈夫です。
