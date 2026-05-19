import http.server, socketserver, os, requests, json

PORT = int(os.environ.get('PORT', 8080))
GROQ_API_KEY = os.environ.get('GROQ_KEY')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA-AVANÇADA - ULTRA</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; display: flex; flex-direction: column; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        #chat { flex: 1; overflow-y: auto; border: 1px solid #0f0; padding: 10px; margin-bottom: 10px; font-size: 16px; min-height: 300px; }
        .controls { display: flex; gap: 10px; padding-bottom: 20px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; font-size: 16px; }
        button { background: #0f0; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        button:disabled { background: #555; }
        .clear-btn { background: #f00; color: #fff; padding: 5px 10px; font-size: 12px; cursor: pointer; border: none; }
    </style>
</head>
<body>
    <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h2 id="status">QI 200 - MODO ULTRA</h2>
        <button class="clear-btn" onclick="localStorage.clear();location.reload()">LIMPAR</button>
    </div>
    <div id="chat"></div>
    <div class="controls">
        <input type="text" id="msg" placeholder="Diga algo..." onkeypress="if(event.key==='Enter') enviar()">
        <button id="btn" onclick="enviar()">ENVIAR</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('msg');
        const btn = document.getElementById('btn');
        const status = document.getElementById('status');
        let historico = JSON.parse(localStorage.getItem('chat_memory')) || [];
        
        function render() {
            chat.innerHTML = '';
            historico.forEach(m => {
                const div = document.createElement('div');
                div.style.marginBottom = '10px';
                div.innerHTML = '<b>' + (m.role==='user'?'VOCÊ':'IA') + ':</b> ' + m.content.replace(/\\n/g, '<br>');
                chat.appendChild(div);
            });
            chat.scrollTop = chat.scrollHeight;
        }

        async function enviar() {
            const text = input.value.trim(); if(!text) return;
            historico.push({ role: 'user', content: text });
            render(); input.value = ''; 
            btn.disabled = true; btn.innerText = 'GERANDO...';
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: historico.slice(-5) })
                });
                const data = await res.json();
                if(data.resposta) {
                    historico.push({ role: 'assistant', content: data.resposta });
                    localStorage.setItem('chat_memory', JSON.stringify(historico));
                    render();
                } else { throw new Error(); }
            } catch (e) {
                const div = document.createElement('div');
                div.style.color = 'red';
                div.innerHTML = '<b>ERRO:</b> A resposta foi longa demais. Tente pedir para ela "continuar de onde parou".';
                chat.appendChild(div);
            } finally {
                btn.disabled = false; btn.innerText = 'ENVIAR';
            }
        }
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
                # Timeout aumentado para 120 segundos para aguentar respostas longas
                res = requests.post(GROQ_URL, 
                    headers={'Authorization': f'Bearer {GROQ_API_KEY}'}, 
                    json={'model': 'llama-3.3-70b-versatile', 'messages': data['messages'], 'max_tokens': 4000},
                    timeout=120)
                resposta = res.json()['choices'][0]['message']['content']
            except:
                resposta = None
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'resposta': resposta}, ensure_ascii=False).encode('utf-8'))

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    httpd.serve_forever()
