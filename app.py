import http.server, socketserver, os, requests, json

PORT = int(os.environ.get('PORT', 8080))
GROQ_API_KEY = os.environ.get('GROQ_KEY')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

SYSTEM_PROMPT = "Você é a SKYNET-BR V6. Responda apenas com a lista solicitada, sem introduções. Seja extremamente rápido e direto."

HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SKYNET V6.1 - GOD SPEED</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; display: flex; flex-direction: column; min-height: 100vh; margin: 0; }
        header { padding: 15px; border-bottom: 1px solid #0f0; display: flex; justify-content: space-between; background: #000; }
        #chat { flex: 1; overflow-y: auto; padding: 20px; background: #000; color: #fff; font-size: 16px; }
        .controls { padding: 20px; background: #000; border-top: 1px solid #0f0; display: flex; gap: 10px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 12px; outline: none; }
        button { background: #0f0; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        button:disabled { background: #333; }
    </style>
</head>
<body>
    <header>
        <span style="text-shadow: 0 0 10px #0f0;">SKYNET-V6.1 [GOD SPEED]</span>
        <button style="background:red; color:white; font-size:10px; cursor:pointer;" onclick="localStorage.clear();location.reload()">PURGE</button>
    </header>
    <div id="chat"></div>
    <div class="controls">
        <input type="text" id="msg" placeholder="COMANDO..." autocomplete="off">
        <button id="btn" onclick="enviar()">EXEC</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('msg');
        const btn = document.getElementById('btn');
        let hist = JSON.parse(localStorage.getItem('skynet_v6')) || [];

        function render() {
            chat.innerHTML = '';
            hist.forEach(function(m) {
                var div = document.createElement('div');
                div.style.marginBottom = '10px';
                var prefixo = m.role == 'user' ? '<b>>> </b>' : '<b>IA: </b>';
                div.innerHTML = prefixo + m.content.replace(/\\n/g, '<br>');
                chat.appendChild(div);
            });
            chat.scrollTop = chat.scrollHeight;
        }

        async function enviar() {
            const v = input.value.trim(); if(!v) return;
            hist.push({role:'user', content:v}); render(); input.value=''; btn.disabled=true;
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({messages: hist.slice(-1)})
                });
                const d = await res.json();
                if(d.resposta) {
                    hist.push({role:'assistant', content:d.resposta});
                    localStorage.setItem('skynet_v6', JSON.stringify(hist));
                    render();
                } else { throw 1; }
            } catch (e) {
                var err = document.createElement('div');
                err.style.color = 'red';
                err.innerHTML = '<b>TIMEOUT:</b> Peça menos itens por vez (ex: 50) para o servidor não travar!';
                chat.appendChild(err);
            } finally { btn.disabled=false; }
        }
        render();
    </script>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/chat':
            l = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(l).decode('utf-8'))
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + data['messages']
            try:
                # O endpoint foi confirmado via busca como sendo o oficial da Groq
                r = requests.post(GROQ_URL, headers={'Authorization': 'Bearer ' + GROQ_API_KEY}, 
                                  json={'model': 'llama-3.3-70b-versatile', 'messages': msgs, 'max_tokens': 3500}, timeout=28)
                resp = r.json()['choices'][0]['message']['content']
            except: resp = None
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'resposta': resp}, ensure_ascii=False).encode())
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode())

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    httpd.serve_forever()
