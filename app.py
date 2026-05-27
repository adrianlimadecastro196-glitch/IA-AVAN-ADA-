import requests
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    GROQ_KEY = os.environ.get('GROQ_KEY') or open('/data/data/com.termux/files/home/groq_key.txt').read().strip()
except:
    GROQ_KEY = os.environ.get('GROQ_KEY', '')

historico = []

PROMPT_SISTEMA = """Voce e a IA-AVANCADA, uma inteligencia artificial de altissimo nivel com raciocinio excepcional equivalente a um QI de 170.
ESPECIALIDADE: Audios subliminares (20 afirmacoes no presente, positivo e 1a pessoa)."""

HTML = b"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IA-AVANCADA</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0a0a0f; color:#fff; font-family:Arial,sans-serif; display:flex; flex-direction:column; height:100vh; }
#header { background:linear-gradient(135deg,#1a1a2e,#16213e); padding:15px; text-align:center; border-bottom:1px solid #00d4ff33; }
#header h1 { color:#00d4ff; font-size:1.4em; }
#temas { display:flex; flex-wrap:wrap; gap:8px; padding:10px 15px; background:#0f0f1a; border-bottom:1px solid #00d4ff22; justify-content:center; }
.tema-btn { background:#1a1a2e; border:1px solid #00d4ff44; color:#00d4ff; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:0.85em; }
#chat { flex:1; overflow-y:auto; padding:15px; display:flex; flex-direction:column; gap:12px; }
.msg { max-width:85%; padding:12px 15px; border-radius:15px; line-height:1.5; font-size:0.95em; white-space:pre-wrap; }
.user { background:linear-gradient(135deg,#00d4ff,#0099bb); color:#000; align-self:flex-end; }
.ia { background:#1a1a2e; border:1px solid #00d4ff33; color:#eee; align-self:flex-start; }
.ia b { color:#00d4ff; display:block; margin-bottom:5px; font-size:0.85em; }
#input-area { background:#1a1a2e; padding:12px; border-top:1px solid #00d4ff33; display:flex; gap:8px; }
#msg { flex:1; background:#0a0a0f; border:1px solid #00d4ff44; color:#fff; padding:10px 15px; border-radius:25px; font-size:1em; outline:none; }
#btn { background:linear-gradient(135deg,#00d4ff,#0099bb); color:#000; border:none; padding:10px 20px; border-radius:25px; font-weight:bold; cursor:pointer; font-size:1em; }
#contador { text-align:center; color:#00d4ff88; font-size:0.75em; padding:4px; background:#0f0f1a; }
</style>
</head>
<body>
<div id="header">
<h1>IA-AVANCADA</h1>
<p>Inteligencia Artificial - QI 170 - Especialista em Subliminares</p>
</div>
<div id="temas">
<button class="tema-btn" onclick="gerarTema('Autoestima')">Autoestima</button>
<button class="tema-btn" onclick="gerarTema('Prosperidade')">Prosperidade</button>
<button class="tema-btn" onclick="gerarTema('Saude')">Saude</button>
<button class="tema-btn" onclick="gerarTema('Foco')">Foco</button>
</div>
<div id="contador">Afirmacoes geradas: <span id="count">0</span></div>
<div id="chat">
<div class="msg ia"><b>IA-AVANCADA</b> Servidor pronto na porta 8080!</div>
</div>
<div id="input-area">
<input id="msg" type="text" placeholder="Digite sua mensagem...">
<button id="btn" onclick="enviar()">Enviar</button>
</div>
<script>
var total = 0;
function enviar() {
  var txt = document.getElementById('msg').value.trim();
  if (!txt) return;
  var chat = document.getElementById('chat');
  chat.innerHTML += '<div class="msg user">' + txt + '</div>';
  document.getElementById('msg').value = '';
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/chat', true);
  xhr.onload = function() {
    var d = JSON.parse(xhr.responseText);
    chat.innerHTML += '<div class="msg ia"><b>IA-AVANCADA</b>' + d.resposta + '</div>';
    chat.scrollTop = chat.scrollHeight;
    total += 20; document.getElementById('count').innerText = total;
  };
  xhr.send('msg=' + encodeURIComponent(txt));
}
function gerarTema(t) { document.getElementById('msg').value = 'Gere 20 afirmacoes sobre ' + t; enviar(); }
</script>
</body>
</html>"""

def perguntar(pergunta):
    historico.append({"role": "user", "content": pergunta})
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": PROMPT_SISTEMA}] + historico[-10:]
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                     headers={"Authorization": "Bearer " + GROQ_KEY}, json=payload).json()
    res = r["choices"][0]["message"]["content"]
    historico.append({"role": "assistant", "content": res})
    return res

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
        self.wfile.write(HTML)
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode()
        params = urllib.parse.parse_qs(body)
        resposta = perguntar(params.get('msg', [''])[0])
        out = json.dumps({"resposta": resposta}).encode('utf-8')
        self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
        self.wfile.write(out)

PORT = 8080
print(f"IA-AVANCADA rodando na porta {PORT}")
HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
