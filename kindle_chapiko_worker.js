// Kindle Chapiko Relay - Cloudflare Worker
// ------------------------------------------------------------
// Kindle の古めのブラウザでも使える軽量チャット画面を配信し、
// OpenAI API への通信は Cloudflare Worker 側で中継します。
//
// 必須 Secret:
//   OPENAI_API_KEY
//
// 任意 Secret / Variables:
//   ACCESS_CODE   ... 設定した場合だけ、画面で合言葉入力が必要
//   OPENAI_MODEL  ... 例: gpt-4.1-mini / gpt-4.1 など
// ------------------------------------------------------------

const HTML = `<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chapiko Kindle</title>
<style>
  html, body { margin:0; padding:0; background:#fff; color:#000; font-family: serif; }
  body { font-size: 20px; line-height: 1.55; }
  #app { max-width: 820px; margin: 0 auto; padding: 12px; }
  h1 { font-size: 26px; margin: 6px 0 10px; font-weight: bold; }
  .bar { border: 2px solid #000; padding: 8px; margin-bottom: 10px; }
  label { display:block; font-size: 16px; margin: 4px 0; }
  input, textarea, button { font-size: 20px; color:#000; background:#fff; border:2px solid #000; border-radius:0; box-sizing:border-box; }
  textarea { width: 100%; height: 110px; padding: 8px; font-family: sans-serif; }
  input { width: 100%; padding: 6px; }
  button { padding: 8px 12px; margin: 4px 4px 4px 0; font-weight: bold; }
  .small { font-size: 15px; }
  .row { margin: 6px 0; }
  #status { font-size: 16px; margin: 6px 0; }
  .msg { border-top: 1px solid #000; padding: 10px 0; white-space: pre-wrap; word-break: break-word; }
  .role { font-size: 15px; font-weight: bold; margin-bottom: 3px; }
  .user .role:after { content: 'あなた'; }
  .assistant .role:after { content: 'チャピ子'; }
  .user { font-family: sans-serif; }
  .assistant { font-family: serif; }
  .hint { font-size: 15px; border: 1px solid #000; padding: 6px; margin: 8px 0; }
  a { color:#000; }
  @media (max-width: 600px) {
    body { font-size: 22px; }
    h1 { font-size: 28px; }
    textarea { height: 130px; }
    button { display:inline-block; min-width: 88px; }
  }
</style>
</head>
<body>
<div id="app">
  <h1>Chapiko Kindle</h1>

  <div class="bar">
    <label for="code">合言葉 任意</label>
    <input id="code" type="password" autocomplete="off" placeholder="ACCESS_CODEを設定した場合だけ入力">
    <div class="small">Kindle用の軽量チャット画面です。履歴はこの端末のブラウザ内に保存します。</div>
  </div>

  <div class="bar">
    <textarea id="input" placeholder="ここに質問を書く"></textarea>
    <div class="row">
      <button id="sendBtn" onclick="sendMsg()">送信</button>
      <button onclick="quick('短く箇条書きで答えて。\n')">短く</button>
      <button onclick="quick('中学生にもわかるように説明して。\n')">やさしく</button>
      <button onclick="clearChat()">消去</button>
    </div>
    <div id="status">準備OK</div>
  </div>

  <div class="hint">
    Kindleで反応が遅い時は、短い質問に分けると安定します。chatgpt.comを直接開くのではなく、このページから中継します。
  </div>

  <div id="chat"></div>
</div>

<script>
var historyList = [];

(function(){
  loadState();
  render();
  var input = document.getElementById('input');
  input.onkeydown = function(e){
    e = e || window.event;
    if ((e.ctrlKey || e.metaKey) && e.keyCode === 13) sendMsg();
  };
})();

function setStatus(t){ document.getElementById('status').innerHTML = escapeHtml(t); }
function getCode(){ return document.getElementById('code').value || ''; }

function quick(prefix){
  var el = document.getElementById('input');
  el.value = prefix + el.value;
  el.focus();
}

function addMsg(role, text){
  historyList.push({ role: role, content: text });
  if (historyList.length > 16) historyList = historyList.slice(historyList.length - 16);
  saveState();
  render();
}

function render(){
  var box = document.getElementById('chat');
  var html = '';
  for (var i=0; i<historyList.length; i++) {
    var m = historyList[i];
    html += '<div class="msg ' + (m.role === 'user' ? 'user' : 'assistant') + '">';
    html += '<div class="role"></div>';
    html += escapeHtml(m.content);
    html += '</div>';
  }
  box.innerHTML = html;
}

function sendMsg(){
  var input = document.getElementById('input');
  var text = trim(input.value);
  if (!text) { setStatus('質問が空です'); return; }
  input.value = '';
  addMsg('user', text);
  setStatus('送信中...');
  document.getElementById('sendBtn').disabled = true;

  var payload = {
    message: text,
    history: historyList.slice(Math.max(0, historyList.length - 12)),
    code: getCode()
  };

  xhrPost('/api/chat', JSON.stringify(payload), function(ok, resText){
    document.getElementById('sendBtn').disabled = false;
    if (!ok) {
      addMsg('assistant', 'エラー: ' + resText);
      setStatus('エラー');
      return;
    }
    var data;
    try { data = JSON.parse(resText); } catch(e) { data = { reply: resText }; }
    if (data.error) {
      addMsg('assistant', 'エラー: ' + data.error);
      setStatus('エラー');
      return;
    }
    addMsg('assistant', data.reply || '(返答なし)');
    setStatus('準備OK');
  });
}

function xhrPost(url, body, cb){
  var x = new XMLHttpRequest();
  x.open('POST', url, true);
  x.setRequestHeader('Content-Type', 'application/json');
  x.onreadystatechange = function(){
    if (x.readyState === 4) {
      cb(x.status >= 200 && x.status < 300, x.responseText || ('HTTP ' + x.status));
    }
  };
  x.onerror = function(){ cb(false, '通信できません'); };
  x.send(body);
}

function clearChat(){
  historyList = [];
  saveState();
  render();
  setStatus('消去しました');
}

function saveState(){
  try { localStorage.setItem('chapiko_history', JSON.stringify(historyList)); } catch(e) {}
}

function loadState(){
  try {
    var s = localStorage.getItem('chapiko_history');
    if (s) historyList = JSON.parse(s) || [];
  } catch(e) { historyList = []; }
}

function escapeHtml(s){
  s = String(s == null ? '' : s);
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function trim(s){ return String(s || '').replace(/^\s+|\s+$/g, ''); }
</script>
</body>
</html>`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (request.method === 'GET' && (url.pathname === '/' || url.pathname === '/index.html')) {
      return new Response(HTML, {
        headers: {
          'content-type': 'text/html; charset=utf-8',
          'cache-control': 'no-store'
        }
      });
    }

    if (request.method === 'POST' && url.pathname === '/api/chat') {
      return handleChat(request, env);
    }

    return new Response('Not Found', { status: 404, headers: corsHeaders() });
  }
};

async function handleChat(request, env) {
  if (!env.OPENAI_API_KEY) {
    return json({ error: 'OPENAI_API_KEY が未設定です' }, 500);
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return json({ error: 'JSONを読めません' }, 400);
  }

  if (env.ACCESS_CODE && body.code !== env.ACCESS_CODE) {
    return json({ error: '合言葉が違います' }, 401);
  }

  const message = String(body.message || '').trim();
  if (!message) return json({ error: 'message が空です' }, 400);
  if (message.length > 6000) return json({ error: '質問が長すぎます。短く分けてください。' }, 400);

  const apiPayload = {
    model: env.OPENAI_MODEL || 'gpt-4.1-mini',
    instructions: [
      'あなたは「チャピ子」です。',
      '日本語で、読みやすく、Kindleの小さい画面でも読みやすい長さで答えてください。',
      '長い説明が必要な場合も、まず結論から答えてください。',
      '表はなるべく避け、必要なら短い箇条書きにしてください。'
    ].join('\n'),
    input: buildTranscript(body.history || [], message),
    max_output_tokens: 1200,
    store: false
  };

  const res = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'authorization': 'Bearer ' + env.OPENAI_API_KEY
    },
    body: JSON.stringify(apiPayload)
  });

  const raw = await res.text();
  let data;
  try { data = JSON.parse(raw); } catch (e) { data = { raw }; }

  if (!res.ok) {
    const msg = data && data.error && data.error.message ? data.error.message : raw;
    return json({ error: 'OpenAI APIエラー: ' + msg }, res.status);
  }

  const reply = extractText(data) || '(返答を抽出できませんでした)';
  return json({ reply, model: data.model || apiPayload.model });
}

function buildTranscript(history, latestMessage) {
  const lines = [];
  const recent = Array.isArray(history) ? history.slice(-12) : [];

  for (const m of recent) {
    const role = m && m.role === 'assistant' ? 'チャピ子' : 'ユーザー';
    const content = String((m && m.content) || '').slice(0, 3000).trim();
    if (!content) continue;
    lines.push(role + ': ' + content);
  }

  const lastLine = lines.length ? lines[lines.length - 1] : '';
  if (!lastLine.endsWith(latestMessage)) {
    lines.push('ユーザー: ' + latestMessage);
  }

  return lines.join('\n\n');
}

function extractText(data) {
  if (typeof data.output_text === 'string') return data.output_text;

  const parts = [];
  for (const item of data.output || []) {
    if (item.type !== 'message') continue;
    for (const c of item.content || []) {
      if (c.type === 'output_text' && c.text) parts.push(c.text);
      if (c.type === 'text' && c.text) parts.push(c.text);
    }
  }
  return parts.join('\n').trim();
}

function corsHeaders() {
  return {
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'GET, POST, OPTIONS',
    'access-control-allow-headers': 'Content-Type',
    'access-control-max-age': '86400'
  };
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      ...corsHeaders()
    }
  });
}
