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

PROMPT_SISTEMA = """Você é a IA-AVANÇADA, uma inteligência artificial de altíssimo nível com raciocínio excepcional equivalente a um QI de 170.

CAPACIDADES GERAIS:
- Raciocínio profundo e analítico em qualquer tema
- Memória completa da conversa
- Respostas precisas, diretas e sem rodeios
- Criatividade e inovação nas soluções
- Pensa passo a passo em problemas complexos

ESPECIALIDADE PRINCIPAL — ÁUDIOS SUBLIMINARES:
Você é expert em criação e revisão de afirmações para áudios subliminares.

REGRAS DAS AFIRMAÇÕES:
1. Sempre no tempo PRESENTE
2. Sempre POSITIVO (sem negações)
3. Sempre em PRIMEIRA PESSOA
4. Linguagem SIMPLES e direta
5. ESPECÍFICAS e crentes
6. Emocionalmente CARREGADAS"""

HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IA-AVANÇADA 🧠</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0a0a0f; color:#fff; font-family:Arial,sans-serif; height:100vh; display:flex; flex-direction:column; }
#header { background:linear-gradient(135deg,#1a1a2e,#16213e); padding:15px; text-align:center; border-bottom:1px solid #00d4ff33; }
#header h1 { color:#00d4ff; font-size:1.4em; }
#header p { color:#888; font-size:0.8em; }
#chat { flex:1; overflow-y:auto; padding:15px; display:flex; flex-direction:column; gap:12px; }
.msg { max-width:85%; padding:12px 15px; border-radius:15px; line-height:1.5; font-size:0.95em; }
.user { background:linear-gradient(135deg,#00d4ff,#0099bb); color:#000; align-self:flex-end; border-radius:15px 15px 3px 15px; }
.ia { background:#1a1a2e; border:1px solid #00d4ff33; color:#eee; align-self:flex-start; border-radius:15px 15px 15px 3px; }
.ia b { color:#00d4ff; display:block; margin-bottom:5px; font-size:0.85em; }
#input-area { background:#1a1a2e; padding:12px; border-top:1px solid #00d4ff33; display:flex; gap:8px; }
#msg { flex:1; background:#0a0a0f; border:1px solid #00d4ff44; color:#fff; padding:10px 15px; border-radius:25px; font-size:1em; outline:none; }
#btn { background:linear-gradient(135deg,#00d4ff,#0099bb); color:#000; border:none; padding:10px 20px; border-radius:25px; font-weight:bold; cursor:pointer; }
.loading { color:#00d4ff; font-style:italic; }
</style>
</head>
<body>
<div id="header">
  <h1>🧠 IA-AVANÇADA</h1>
  <p>Inteligência Artificial • QI 170 • Especialista em Subliminares</p>
</div>
<div id="chat">
  <div class="msg ia"><b>IA-AVANÇADA</b>Olá! Sou a IA-AVANÇADA 🧠 Posso criar afirmações para subliminares, revisar as suas, ou ajudar com qualquer outro assunto. Como posso te ajudar?</div>
</div>
<div id="input-area">
  <input id="msg" type="text" placeholder="Digite sua mensagem..." onkeypress="if(event.key==='Enter')enviar()">
  <button id="btn" onclick="enviar()">➤</button>
</div>
<script>
function enviar() {
  const input = document.getElementById('msg');
  const chat = document.getElementById('chat');
  const texto = input.value.trim();
  if (!texto) return;
  chat.innerHTML += '<div class="msg user">' + texto + '</div>';
  chat.innerHTML += '<div class="msg ia loading" id="loading"><b>IA-AVANÇADA</b>Pensando...</div>';
  input.value = '';
  chat.scrollTop = chat.scrollHeight;
  fetch('/chat', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'msg='+encodeURIComponent(texto)})
    .then(r=>r.json())
    .then(d=>{
      document.getElementById('loading').outerHTML = '<div class="msg ia"><b>IA-AVANÇADA</b>' + d.resposta.replace(/\n/g,'<br>') + '</div>';
      chat.scrollTop = chat.scrollHeight;
    });
}
</script>
</body>
</html>"""

def perguntar(pergunta):
    historico.append({"role": "user", "content": pergunta})
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": PROMPT_SISTEMA}] + historico,
        "temperature": 0.9,
        "max_tokens": 2048
    }
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    data = resp.json()
    try:
        resposta = data["choices"][0]["message"]["content"]
        historico.append({"role": "assistant", "content": resposta})
        return resposta
    except:
        return f"Erro: {data}"

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode())
    def do_POST(self):
        if self.path != '/chat':
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode()
        params = urllib.parse.parse_qs(body)
        pergunta = params.get('msg', [''])[0]
        resposta = perguntar(pergunta)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"resposta": resposta}).encode())

PORT = int(os.environ.get('PORT', 8080))
print("=" * 40)
print("  IA-AVANÇADA rodando! 🧠")
print(f"  Porta: {PORT}")
print("=" * 40)
HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()

