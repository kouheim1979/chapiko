# チャピ子 オンライン表示中継

Kindleで見やすい入口ページです。

## 開くURL

```text
https://kouheim1979.github.io/chapiko/
```

## 方式

VDO.Ninja の `push` と `view` のリンクを作ります。

- ローカルサーバーなし
- OpenAI APIキーなし
- Cloudflare Workerなし
- 送信側は `push` リンク
- 表示側は `view` リンク

## 使い方

1. PCまたはスマホで上のURLを開く
2. 「部屋IDを作る」を押す
3. 送信側の端末で「送信側を開く」を押す
4. 表示側の端末で同じ部屋IDを入れて「表示側を開く」を押す

## 注意

表示側の端末ブラウザがWebRTCに対応していない場合は映らないことがあります。

## ファイル

```text
index.html                         VDO.Ninjaリンク作成ページ
.github/workflows/pages.yml        GitHub Pages自動デプロイ
README.md                          この説明
```
