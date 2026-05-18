import http.server
import socketserver
import os
import requests
import json
import urllib.parse

PORT = int(os.environ.get("PORT", 8080))
GROQ_API_KEY = os.environ.get("GROQ_KEY")

HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA-AVANÇADA</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; display: flex; flex-direction: column; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        #chat { flex: 1; overflow-y: auto; border: 1px solid #0f0; padding: 10px; margin-bottom: 10px; font-size: 16px; }
        .controls { display: flex; gap: 10px; padding-bottom: 20px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; font-size: 16px; }
        button { background: #0f0; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        .theme-btn { background: #333; color: #fff; margin-bottom: 5px; font-size: 12px; }
    </style>
</head>
<body>
    <div style="display:flex; justify-content: space-between; align-items: center;">
        <h2 style="margin:0">QI 200 - ONLINE</h2>
        <div style="display:flex; flex-direction:column">
            <button class="theme-btn" onclick="setTheme('autoestima')">Autoestima</button>
            <button class="theme-btn" onclick="setTheme('foco')">Foco</button>
        </div>
    </div>
    <div id="chat"></div>
    <div class="controls">
        <input type="text" id="msg" placeholder="Mensagem..." onkeypress="if(event.key==='Enter') enviar()">
        <button id="btn" onclick="enviar()">ENVIAR</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('msg');
        const btn = document.getElementById('btn');
        function append(text, sender) {
            const div = document.createElement('div');
            div.style.marginBottom = '10px';
            div.innerHTML = `<b>\({sender}:</b> \){text.replace(/\\n/g, '<br>')}`;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        async function enviar() {
            const text = input.value.trim();
            if(!text) return;
            append(text, 'VOCÊ');
            input.value = '';
            btn.disabled = true;
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: 'msg=' + encodeURIComponent(text)
                });
                const data = await res.json();
                append(data.resposta, 'IA');
            } catch (e) {
                append('Erro na conexão.', 'SISTEMA');
            } finally {
                btn.disabled = false;
            }
        }
        function setTheme(t) { input.value = 'Quero afirmações sobre ' + t; enviar(); }
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
            data = self.rfile.read(length).decode('utf-8')
            params = urllib.parse.parse_qs(data)
            msg = params.get('msg', [''])[0]
            
            res_text = self.call_groq(msg)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'resposta': res_text}, ensure_ascii=False).encode('utf-8'))

    def call_groq(self, text):
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": text}]
                }
            )
            return r.json()['choices'][0]['message']['content']
        except:
            return "Erro ao falar com a IA."

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
