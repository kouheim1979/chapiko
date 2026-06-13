# チャピ子 Kindle

Kindleで見やすい入口ページです。

## 開くURL

```text
https://kouheim1979.github.io/chapiko/
```

## 自分専用LLM チャピ子

```text
https://kouheim1979.github.io/chapiko/my-hf-llm.html
```

Hugging Face Hubに置いたWebLLM/MLC形式モデルを、GitHub Pagesから読み込んでブラウザ内で動かすページです。

構成:

```text
Hugging Face Hub
→ 自分用モデル/量子化モデルを置く

GitHub Pages
→ チャピ子画面

WebLLM
→ PC/スマホのブラウザ内で動かす
```

注意:

- Hugging Faceに置くモデルはWebLLM/MLC形式が必要です。
- GGUFをそのまま置いただけでは動きません。
- ベースライブラリは、モデルの元になった系統に合わせます。
- WebGPU対応ブラウザが必要です。
- Kindleでは厳しいのでPC/スマホ向けです。

## 無料LLM横断 チャピ子ハブ

```text
https://kouheim1979.github.io/chapiko/free-llm-hub.html
```

APIキーなしで、複数の無料LLMを横断比較するページです。

追加したモデル系統:

```text
チャピ子ミニ
SmolLM2
Qwen 2.5
Qwen 3 / 3.5
Qwen Coder
Llama 3.2 / 3.1
Hermes
Gemma / Gemma JPN
Phi 3.5 / Phi 4 mini
Mistral
OpenHermes
WizardMath
DeepSeek R1 Distill Qwen
OLMo
```

モデル本体はGitHubに置いていません。WebLLM/Hugging Face側から取得し、推論はブラウザ内で行います。

便利ボタン:

```text
軽量おすすめ
日本語寄り
技術/コード寄り
全部選択
全部解除
```

注意:

- WebLLMはWebGPU対応ブラウザが必要です。
- 8B/9B級モデルはかなり重いです。
- KindleではWebLLMは厳しいので、Kindleは簡易LLMを使う想定です。

## 簡易LLM チャピ子ミニ

```text
https://kouheim1979.github.io/chapiko/simple-llm.html
```

これは本物の大規模LLMではありません。GitHub Pagesだけで動く、API不要・無料の簡易チャットです。

できること:

- キーワードに近い内蔵知識を返す
- 端末内の localStorage に「学習メモ」を保存する
- Kindle向けに白黒・大文字・軽量HTMLで表示する
- OpenAI APIキーなしで動く

## オンライン表示中継

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
my-hf-llm.html                     自分専用Hugging Faceモデル用ページ
free-llm-hub.html                  無料LLM横断ページ
simple-llm.html                    APIなし簡易チャット
.github/workflows/pages.yml        GitHub Pages自動デプロイ
README.md                          この説明
```
