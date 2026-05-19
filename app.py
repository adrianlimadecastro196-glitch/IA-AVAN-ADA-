import http.server
import socketserver
import os
import requests
import json
import urllib.parse

PORT = int(os.environ.get('PORT', 8080))
GROQ_API_KEY = os.environ.get('GROQ_KEY')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA-AVANÇADA - MODO TURBO</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; display: flex; flex-direction: column; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        #chat { flex: 1; overflow-y: auto; border: 1px solid #0f0; padding: 10px; margin-bottom: 10px; font-size: 16px; min-height: 300px; }
        .controls { display: flex; gap: 10px; padding-bottom: 20px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; font-size: 16px; }
        button { background: #0f0; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        .clear-btn { background: #f00; color: #fff; padding: 5px 10px; font-size: 12px; cursor: pointer; border: none; }
    </style>
</head>
<body>
    <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h2 style="margin:0">QI 200 - TURBO</h2>
        <button class="clear-btn" onclick="limparChat()">LIMPAR</button>
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
        let historico = JSON.parse(localStorage.getItem('chat_memory')) || [];
        function salvar() { localStorage.setItem('chat_memory', JSON.stringify(historico)); }
        function render() {
            chat.innerHTML = '';
            historico.forEach(m => appendToScreen(m.content, m.role === 'user' ? 'VOCÊ' : 'IA'));
        }
        function appendToScreen(text, sender) {
            const div = document.createElement('div');
            div.style.marginBottom = '10px';
            div.innerHTML = '<b>' + sender + ':</b> ' + text.split('\\n').join('<br>');
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        async function enviar() {
            const text = input.value.trim();
            if(!text) return;
            historico.push({ role: 'user', content: text });
            render(); salvar();
            input.value = ''; btn.disabled = true;
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: historico })
                });
                const data = await res.json();
                historico.push({ role: 'assistant', content: data.resposta });
                render(); salvar();
            } catch (e) {
                appendToScreen('Erro na conexão.', 'SISTEMA');
            } finally { btn.disabled = false; }
        }
        function limparChat() {
            if(confirm('Limpar toda a conversa?')) {
                historico = []; salvar(); render();
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
            messages = data.get('messages', [])
            res_text = self.call_groq(messages)
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'resposta': res_text}, ensure_ascii=False).encode('utf-8'))
    def call_groq(self, messages):
        try:
            r = requests.post(GROQ_URL, headers={'Authorization': f'Bearer {GROQ_API_KEY}'}, json={'model': 'llama-3.3-70b-versatile', 'messages': messages, 'max_tokens': 8000})
            return r.json()['choices'][0]['message']['content']
        except: return "Erro ao falar com a IA."

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    httpd.serve_forever()
