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

CAPACIDADES GERAIS:
- Raciocinio profundo e analitico em qualquer tema
- Memoria completa da conversa
- Respostas precisas, diretas e sem rodeios
- Criatividade e inovacao nas solucoes

ESPECIALIDADE PRINCIPAL - AUDIOS SUBLIMINARES:
Quando receber um tema, gere exatamente 20 afirmacoes poderosas.

REGRAS DAS AFIRMACOES:
1. Sempre no tempo PRESENTE
2. Sempre POSITIVO (sem negacoes)
3. Sempre em PRIMEIRA PESSOA
4. Linguagem SIMPLES e direta
5. ESPECIFICAS e crentes
6. Emocionalmente CARREGADAS"""

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
#header p { color:#888; font-size:0.8em; }
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
<button class="tema-btn" onclick="gerarTema('Prosperidade e dinheiro')">Prosperidade</button>
<button class="tema-btn" onclick="gerarTema('Saude e bem-estar')">Saude</button>
<button class="tema-btn" onclick="gerarTema('Amor e relacionamentos')">Amor</button>
<button class="tema-btn" onclick="gerarTema('Foco e produtividade')">Foco</button>
<button class="tema-btn" onclick="gerarTema('Emagrecimento e corpo ideal')">Corpo</button>
<button class="tema-btn" onclick="gerarTema('Inteligencia e memoria')">Inteligencia</button>
<button class="tema-btn" onclick="gerarTema('Paz interior e ansiedade')">Paz</button>
</div>
<div id="contador">Afirmacoes geradas: <span id="count">0</span></div>
<div id="chat">
<div class="msg ia"><b>IA-AVANCADA</b>Ola! Clique em um tema acima para gerar 20 afirmacoes poderosas, ou digite sua mensagem abaixo!</div>
</div>
<div id="input-area">
<input id="msg" type="text" placeholder="Digite sua mensagem...">
<button id="btn">Enviar</button>
</div>
<script>
var total = 0;
document.getElementById('btn').addEventListener('click', enviar);
document.getElementById('msg').addEventListener('keydown', function(e){ if(e.key==='Enter') enviar(); });
function gerarTema(tema) {
  document.getElementById('msg').value = 'Gere 20 afirmacoes poderosas para subliminar sobre: ' + tema;
  enviar();
}
function enviar() {
  var txt = document.getElementById('msg').value.trim();
  if (!txt) return;
  var chat = document.getElementById('chat');
  chat.innerHTML += '<div class="msg user">' + txt + '</div>';
  document.getElementById('msg').value = '';
  chat.innerHTML += '<div class="msg ia" id="loading"><b>IA-AVANCADA</b>Processando... (pode levar ate 60s na primeira mensagem)</div>';
  chat.scrollTop = chat.scrollHeight;
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/chat', true);
  xhr.timeout = 120000;
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
    var d = JSON.parse(xhr.responseText);
    var resp = d.resposta;
    document.getElementById('loading').outerHTML = '<div class="msg ia"><b>IA-AVANCADA</b>' + resp + '</div>';
    var linhas = resp.split('\n');
    linhas.forEach(function(l){ if(l.match(/^\d+\./)) total++; });
    document.getElementById('count').innerText = total;
    document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
  };
  xhr.ontimeout = function() {
    document.getElementById('loading').outerHTML = '<div class="msg ia"><b>IA-AVANCADA</b>Tempo esgotado. Tente novamente!</div>';
  };
  xhr.send('msg=' + encodeURIComponent(txt));
}
</script>
</body>
</html>"""

def perguntar(pergunta):
    historico.append({"role": "user", "content": pergunta})
    hdrs = {"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": PROMPT_SISTEMA}] + historico,
        "temperature": 0.9,
        "max_tokens": 2048
    }
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=hdrs, json=payload)
    data = resp.json()
    try:
        resposta = data["choices"][0]["message"]["content"]
        historico.append({"role": "assistant", "content": resposta})
        return resposta
    except:
        return "Erro: " + str(data)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML)
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
        out = json.dumps({"resposta": resposta}).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', str(len(out)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(out)

PORT = int(os.environ.get('PORT', 8080))
print("IA-AVANCADA rodando na porta", PORT)
HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()

