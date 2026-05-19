import http.server, socketserver, os, requests, json

PORT = int(os.environ.get('PORT', 8080))
GROQ_API_KEY = os.environ.get('GROQ_KEY')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA-AVANÇADA - V4 ULTRA</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; display: flex; flex-direction: column; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        #chat { flex: 1; overflow-y: auto; border: 1px solid #0f0; padding: 15px; margin-bottom: 10px; font-size: 16px; background: rgba(0,20,0,0.5); }
        .controls { display: flex; gap: 10px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; font-size: 16px; outline: none; }
        button { background: #0f0; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:disabled { background: #333; color: #777; }
        .clear-btn { background: #f00; color: #fff; padding: 5px 15px; font-size: 14px; cursor: pointer; border: none; }
        .msg-ia { color: #fff; margin-bottom: 15px; border-left: 3px solid #0f0; padding-left: 10px; }
        .msg-user { color: #0f0; margin-bottom: 15px; text-align: right; border-right: 3px solid #0f0; padding-right: 10px; }
    </style>
</head>
<body>
    <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h2 style="margin:0; color:#0f0;">QI 200 - V4</h2>
        <button class="clear-btn" onclick="limpar()">LIMPAR MEMÓRIA</button>
    </div>
    <div id="chat"></div>
    <div class="controls">
        <input type="text" id="msg" placeholder="Diga algo..." autocomplete="off">
        <button id="btn" onclick="enviar()">ENVIAR</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('msg');
        const btn = document.getElementById('btn');
        let historico = JSON.parse(localStorage.getItem('ia_v4_mem')) || [];

        function render() {
            chat.innerHTML = '';
            historico.forEach(m => {
                const div = document.createElement('div');
                div.className = m.role === 'user' ? 'msg-user' : 'msg-ia';
                div.innerHTML = '<b>' + (m.role==='user'?'VOCÊ':'IA') + ':</b><br>' + m.content.replace(/\\n/g, '<br>');
                chat.appendChild(div);
            });
            chat.scrollTop = chat.scrollHeight;
        }

        async function enviar() {
            const val = input.value.trim(); if(!val) return;
            historico.push({ role: 'user', content: val });
            render(); input.value = ''; btn.disabled = true;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: historico.slice(-3) }) 
                });
                const data = await res.json();
                if(data.resposta) {
                    historico.push({ role: 'assistant', content: data.resposta });
                    localStorage.setItem('ia_v4_mem', JSON.stringify(historico));
                    render();
                } else { throw new Error(); }
            } catch (e) {
                const err = document.createElement('div');
                err.style.color = 'yellow';
                err.innerHTML = '<b>DICA:</b> O servidor demorou muito. Clique em "LIMPAR MEMÓRIA" e peça menos coisas de cada vez!';
                chat.appendChild(err);
            } finally { btn.disabled = false; }
        }

        function limpar() {
            if(confirm('Apagar histórico para ficar mais leve?')) {
                localStorage.removeItem('ia_v4_mem');
                historico = []; render();
            }
        }
        input.addEventListener('keypress', (e) => { if(e.key==='Enter') enviar(); });
        render();
    </script>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode('utf-8'))
    def do_POST(self):
        if self.path == '/chat':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            try:
                # Timeout de 28 segundos para não estourar os 30 do Render
                res = requests.post(GROQ_URL, 
                    headers={'Authorization': f'Bearer {GROQ_API_KEY}'}, 
                    json={'model': 'llama-3.3-70b-versatile', 'messages': data['messages'], 'max_tokens': 2000},
                    timeout=28)
                resposta = res.json()['choices'][0]['message']['content']
            except: resposta = None
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'resposta': resposta}, ensure_ascii=False).encode('utf-8'))

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    httpd.serve_forever()
