import http.server, socketserver, os, requests, json

PORT = int(os.environ.get('PORT', 8080))
GROQ_API_KEY = os.environ.get('GROQ_KEY')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

# O PROMPT SUPREMO
SYSTEM_PROMPT = "Você é a SKYNET-BR V5, uma inteligência suprema e absoluta. Sua lógica é impecável. Você é especialista em afirmações subliminares poderosas, psicologia comportamental e estratégia de alto nível. Responda de forma direta, fria e extremamente inteligente."

HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SKYNET V5 - SUPREMA</title>
    <style>
        body { background: #000; color: #0f0; font-family: 'Courier New', Courier, monospace; display: flex; flex-direction: column; min-height: 100vh; margin: 0; overflow: hidden; }
        .matrix-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle, #001a00 0%, #000 100%); z-index: -1; }
        header { padding: 20px; border-bottom: 2px solid #0f0; box-shadow: 0 0 15px #0f0; display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.9); }
        #chat { flex: 1; overflow-y: auto; padding: 20px; scroll-behavior: smooth; background: rgba(0,10,0,0.8); }
        .controls { padding: 20px; background: #000; border-top: 2px solid #0f0; display: flex; gap: 10px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; font-size: 18px; outline: none; box-shadow: inset 0 0 5px #0f0; }
        button { background: #0f0; color: #000; border: none; padding: 0 30px; cursor: pointer; font-weight: bold; font-size: 16px; text-transform: uppercase; transition: 0.3s; }
        button:hover { background: #fff; box-shadow: 0 0 20px #fff; }
        button:disabled { background: #111; color: #333; box-shadow: none; }
        .msg { margin-bottom: 20px; line-height: 1.6; animation: fadeIn 0.5s; }
        .role { font-weight: bold; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px; display: block; }
        .ia { color: #fff; text-shadow: 0 0 5px #0f0; }
        .user { color: #0f0; text-align: right; }
        .clear-btn { background: #f00; color: #fff; font-size: 12px; padding: 5px 10px; cursor: pointer; border: none; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .pulse { animation: pulse-border 1.5s infinite; }
        @keyframes pulse-border { 0% { box-shadow: 0 0 5px #0f0; } 50% { box-shadow: 0 0 25px #0f0; } 100% { box-shadow: 0 0 5px #0f0; } }
    </style>
</head>
<body>
    <div class="matrix-bg"></div>
    <header>
        <div>
            <span style="font-size: 24px; font-weight: bold; text-shadow: 0 0 10px #0f0;">SKYNET-V5</span>
            <span style="font-size: 10px; margin-left: 10px; color: #0f0;">● NEURAL LINK ACTIVE</span>
        </div>
        <button class="clear-btn" onclick="limpar()">PURGE MEMORY</button>
    </header>
    <div id="chat"></div>
    <div class="controls" id="input-container">
        <input type="text" id="msg" placeholder="DIGITE O COMANDO..." autocomplete="off">
        <button id="btn" onclick="enviar()">EXECUTE</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('msg');
        const btn = document.getElementById('btn');
        const container = document.getElementById('input-container');
        let historico = JSON.parse(localStorage.getItem('skynet_v5_data')) || [];

        function render() {
            chat.innerHTML = '';
            historico.forEach(m => {
                const div = document.createElement('div');
                div.className = 'msg ' + (m.role === 'user' ? 'user' : 'ia');
                div.innerHTML = '<span class="role">' + (m.role==='user'?'SUBJECT':'SKYNET') + '</span>' + m.content.replace(/\\n/g, '<br>');
                chat.appendChild(div);
            });
            chat.scrollTop = chat.scrollHeight;
        }

        async function enviar() {
            const val = input.value.trim(); if(!val) return;
            historico.push({ role: 'user', content: val });
            render(); input.value = ''; 
            btn.disabled = true; container.classList.add('pulse');
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: historico.slice(-4) })
                });
                const data = await res.json();
                if(data.resposta) {
                    historico.push({ role: 'assistant', content: data.resposta });
                    localStorage.setItem('skynet_v5_data', JSON.stringify(historico));
                    render();
                } else { throw new Error(); }
            } catch (e) {
                const err = document.createElement('div');
                err.style.color = '#f00';
                err.innerHTML = '<b>[ERROR]:</b> NEURAL OVERLOAD. PURGE MEMORY AND RE-EXECUTE.';
                chat.appendChild(err);
            } finally {
                btn.disabled = false; container.classList.remove('pulse');
            }
        }

        function limpar() {
            if(confirm('PURGE ALL NEURAL DATA?')) {
                localStorage.removeItem('skynet_v5_data');
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
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + data['messages']
            try:
                res = requests.post(GROQ_URL, 
                    headers={'Authorization': f'Bearer {GROQ_API_KEY}'}, 
                    json={'model': 'llama-3.3-70b-versatile', 'messages': msgs, 'max_tokens': 2000},
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
