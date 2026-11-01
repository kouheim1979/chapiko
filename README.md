# チャピ子 Kindle

Kindleで見やすい入口ページです。

## 開くURL

```text
https://kouheim1979.github.io/chapiko/
```

## 外部サーバLLM チャピ子

```text
https://kouheim1979.github.io/chapiko/external-server-llm.html
```

モデルと推論は外部サーバ（Hugging Face Space 無料CPU）、GitHub Pagesは画面だけにする方式です。APIキー不要・無料で、本物のLLMが使えます。画面はES5 + XMLHttpRequestだけで書いてあるので、古いKindleブラウザでも動く想定です（実機での確認はこれから）。

複数のHugging Face Spaceを登録できます。

```text
Space 1: 最小API・接続確認
Space 2: 軽量LLM（Qwen2.5 0.5B）
Space 3: 予備または別モデル
GitHub Pages: 上から順に接続 / 全部に質問
```

### 実現までの手順

1. **Space 1（最小API）を作る** — 数十秒でビルドできる接続確認用
   - Hugging Faceで New Space → SDK `Docker` → `Blank` → `CPU basic (free)`
   - `hf-space-minimal-template/` の4ファイル（`README.md` `app.py` `requirements.txt` `Dockerfile`）をアップロード
   - `https://<ユーザー名>-<Space名>.hf.space/health` が `{"ok":true,"status":"ready",...}` になればOK
2. **画面から接続する**
   - `external-server-llm.html` の「外部サーバ設定」に、SpaceページのURL（`https://huggingface.co/spaces/<ユーザー名>/<Space名>`）か `<ユーザー名>/<Space名>` を貼る（`.hf.space` のURLへ自動変換）
   - 「接続テスト」→ 質問して、最小APIの返事が来ればGitHub Pages ↔ Space の通信は完成
3. **Space 2（軽量LLM）を作る**
   - 同じ手順で `hf-space-template/` の4ファイルをアップロード（初回ビルド5〜10分）
   - Running後、モデルを裏で読み込みます。画面の「起こす」で「準備OK」まで待つ
   - 公開Spaceは誰でも叩けるので、Settings → Variables and secrets → New secret で `ACCESS_CODE` を設定し、画面の「合言葉」に同じ値を入れるのがおすすめ
4. **Kindleで使う**
   - PCで設定後「Kindle用URLを作る」を押し、出てきたURLをKindleのブラウザで開く（Space設定が入った状態で始まる。合言葉は手入力）

### うまくいかない時

```text
接続できません      → スリープ中 / ビルド中 / URL間違い。「起こす」かSpaceページを開く
モデル読み込み中    → 起動直後。「起こす」で準備OKまで待つ（1〜3分）
合言葉が違います    → Spaceの ACCESS_CODE と画面の合言葉を合わせる
タイムアウト        → 無料CPUで回答が長すぎる。Spaceの MAX_NEW_TOKENS を下げる
```

注意:

- 無料CPU Spaceは遅いです（0.5Bモデルで1回答に数十秒）。
- 無料Spaceは48時間使わないとスリープします。スリープ明けはビルド済みでもモデル読み込みに1〜3分かかります。
- 複数Spaceは大きいLLMの合体ではなく、逃げ道・役割分担です。
- モデルやトークン数はSpaceのVariablesで変えられます。詳しくは `hf-space-template/README.md`。

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
external-server-llm.html           外部サーバLLM用の画面（Kindle対応の軽量版）
hf-space-minimal-template/         Hugging Face Space用 最小APIテンプレート（4ファイルをそのままSpaceへ）
hf-space-template/                 Hugging Face Space用 LLMテンプレート（transformers CPU / 4ファイルをそのままSpaceへ）
my-hf-llm.html                     自分専用Hugging Faceモデル用ページ
free-llm-hub.html                  無料LLM横断ページ
simple-llm.html                    APIなし簡易チャット
.github/workflows/pages.yml        GitHub Pages自動デプロイ
README.md                          この説明
```
