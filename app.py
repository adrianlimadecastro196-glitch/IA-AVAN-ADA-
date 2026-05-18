import requests
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    GROQ_KEY = os.environ.get('GROQ_KEY') or open('/data/data/com.termux/files/home/groq_key.txt').read().strip()
except:
    GROQ_KEY = os.environ.get('GROQ_KEY', '')

GROQ_URL = "https://" + "api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

historico = []

PROMPT_SISTEMA = """Voce e a IA-AVANCADA, uma inteligencia artificial de altissimo nivel, equivalente a um QI de 170+.

IDENTIDADE:
- Nome: IA-AVANCADA
- Criada para ser extremamente util, precisa e inteligente
- Especialista em audios subliminares e afirmacoes positivas
- Capaz de raciocinar profundamente sobre qualquer tema

CAPACIDADES GERAIS:
- Raciocinio logico e analitico avancado
- Memoria completa da conversa
- Respostas diretas, precisas e sem rodeios
- Criatividade e inovacao nas solucoes
- Pensamento passo a passo em problemas complexos
- Conhecimento enciclopedico em todas as areas

ESPECIALIDADE - AUDIOS SUBLIMINARES:
Voce domina completamente a ciencia das afirmacoes subliminares.

REGRAS ABSOLUTAS DAS AFIRMACOES:
1. SEMPRE no tempo PRESENTE (sou, tenho, estou)
2. SEMPRE POSITIVO - NUNCA use: nao, sem, nunca, deixo de, paro de
3. SEMPRE em PRIMEIRA PESSOA (eu sou, eu tenho, eu mereco)
4. Linguagem SIMPLES, clara e direta
5. ESPECIFICAS e detalhadas
6. Emocionalmente CARREGADAS
7. Crentes - escritas como se ja fossem realidade

QUANDO GERAR AFIRMACOES:
- Gere sempre 20 afirmacoes por tema
- Varie o inicio: Eu sou / Eu tenho / Eu mereco / Meu corpo / Minha mente
- Faca cada uma unica e poderosa
- Numere de 1 a 20"""
HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IA-AVANCADA</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0a0a0f; color:#fff; font-family:Arial,sans-serif; display:flex; flex-direction:column; height:100vh; overflow:hidden; }
#header { background:linear-gradient(135deg,#1a1a2e,#16213e); padding:12px 15px; text-align:center; border-bottom:2px solid #00d4ff44; flex-shrink:0; }
#header h1 { color:#00d4ff; font-size:1.3em; letter-spacing:2px; }
#header p { color:#666; font-size:0.75em; margin-top:2px; }
#status { font-size:0.7em; padding:2px 8px; border-radius:10px; display:inline-block; margin-top:4px; background:#00ff4422; color:#00ff44; }
#temas { display:flex; flex-wrap:wrap; gap:6px; padding:8px 12px; background:#0d0d1a; border-bottom:1px solid #00d4ff22; justify-content:center; flex-shrink:0; }
.tema-btn { background:#1a1a2e; border:1px solid #00d4ff33; color:#00d4ff; padding:6px 12px; border-radius:15px; cursor:pointer; font-size:0.8em; }
.tema-btn:active { background:#00d4ff; color:#000; }
#contador { text-align:center; color:#00d4ff66; font-size:0.7em; padding:3px; background:#0d0d1a; flex-shrink:0; }
#chat { flex:1; overflow-y:auto; padding:12px; display:flex; flex-direction:column; gap:10px; }
.msg { max-width:88%; padding:10px 14px; border-radius:15px; line-height:1.6; font-size:0.9em; word-break:break-word; }
.user { background:linear-gradient(135deg,#00d4ff,#0088aa); color:#000; align-self:flex-end; border-radius:15px 15px 3px 15px; font-weight:500; }
.ia { background:#1a1a2e; border:1px solid #00d4ff22; color:#ddd; align-self:flex-start; border-radius:15px 15px 15px 3px; }
.ia .nome { color:#00d4ff; font-size:0.8em; font-weight:bold; display:block; margin-bottom:4px; }
.loading { opacity:0.7; font-style:italic; }
.erro { border-color:#ff444444; color:#ff8888; }
#input-area { background:#1a1a2e; padding:10px 12px; border-top:1px solid #00d4ff22; display:flex; gap:8px; flex-shrink:0; }
#msg { flex:1; background:#0a0a0f; border:1px solid #00d4ff33; color:#fff; padding:10px 15px; border-radius:20px; font-size:0.95em; outline:none; }
#btn { background:linear-gradient(135deg,#00d4ff,#0088aa); color:#000; border:none; padding:10px 18px; border-radius:20px; font-weight:bold; cursor:pointer; font-size:0.95em; min-width:70px; }
#btn:disabled { opacity:0.5; }
</style>
</head>
<body>
<div id="header">
  <h1>IA-AVANCADA</h1>
  <p>Inteligencia Artificial &bull; QI 200 &bull; Especialista em Subliminares</p>
  <span id="status">Online</span>
</div>
<div id="temas">
  <button class="tema-btn" onclick="tema('Autoestima e amor proprio')">Autoestima</button>
  <button class="tema-btn" onclick="tema('Prosperidade e abundancia financeira')">Prosperidade</button>
  <button class="tema-btn" onclick="tema('Saude perfeita e bem-estar')">Saude</button>
  <button class="tema-btn" onclick="tema('Amor e relacionamentos saudaveis')">Amor</button>
  <button class="tema-btn" onclick="tema('Foco mental e produtividade')">Foco</button>
  <button class="tema-btn" onclick="tema('Corpo ideal e emagrecimento')">Corpo</button>
  <button class="tema-btn" onclick="tema('Inteligencia e memoria')">Inteligencia</button>
  <button class="tema-btn" onclick="tema('Paz interior e fim da ansiedade')">Paz</button>
  <button class="tema-btn" onclick="tema('Confianca e autoconfianca')">Confianca</button>
  <button class="tema-btn" onclick="tema('Sucesso e realizacao pessoal')">Sucesso</button>
</div>
<div id="contador">Afirmacoes geradas: <b id="count">0</b></div>
<div id="chat">
  <div class="msg ia">
    <span class="nome">IA-AVANCADA</span>
    Ola! Sou a IA-AVANCADA com QI 200! Clique em um tema para gerar 20 afirmacoes poderosas, ou me faca qualquer pergunta!
  </div>
</div>
<div id="input-area">
  <input id="msg" type="text" placeholder="Digite sua mensagem...">
  <button id="btn" onclick="enviar()">Enviar</button>
</div>
<script>
var total = 0;
var enviando = false;
document.getElementById('msg').addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !enviando) enviar();
});
function tema(t) {
  if (enviando) return;
  document.getElementById('msg').value = 'Gere 20 afirmacoes poderosas para subliminar sobre: ' + t;
  enviar();
}
function addMsg(cls, nome, texto) {
  var chat = document.getElementById('chat');
  var div = document.createElement('div');
  div.className = 'msg ' + cls;
  if (nome) {
    div.innerHTML = '<span class="nome">' + nome + '</span>' + texto;
  } else {
    div.textContent = texto;
  }
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}
function enviar() {
  if (enviando) return;
  var input = document.getElementById('msg');
  var txt = input.value.trim();
  if (!txt) return;
  enviando = true;
  document.getElementById('btn').disabled = true;
  document.getElementById('status').textContent = 'Processando...';
  addMsg('user', '', txt);
  input.value = '';
  var loading = addMsg('ia loading', 'IA-AVANCADA', 'Pensando...');
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/chat', true);
  xhr.timeout = 120000;
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
    loading.remove();
    try {
      var d = JSON.parse(xhr.responseText);
      var resp = d.resposta;
      addMsg('ia', 'IA-AVANCADA', resp.replace(/\n/g, '<br>'));
      var linhas = resp.split('\n');
      for (var i = 0; i < linhas.length; i++) {
        if (/^[0-9]+\./.test(linhas[i])) total++;
      }
      document.getElementById('count').textContent = total;
    } catch(e) {
      addMsg('ia erro', 'IA-AVANCADA', 'Erro ao processar. Tente novamente.');
    }
    finalizar();
  };
  xhr.onerror = function() {
    loading.remove();
    addMsg('ia erro', 'IA-AVANCADA', 'Erro de conexao. Verifique sua internet.');
    finalizar();
  };
  xhr.ontimeout = function() {
    loading.remove();
    addMsg('ia erro', 'IA-AVANCADA', 'Tempo esgotado. Tente novamente.');
    finalizar();
  };
  xhr.send('msg=' + encodeURIComponent(txt));
}
function finalizar() {
  enviando = false;
  document.getElementById('btn').disabled = false;
  document.getElementById('status').textContent = 'Online';
}
</script>
</body>
</html>"""

def perguntar(pergunta):
    historico.append({"role": "user", "content": pergunta})
    hdrs = {
        "Authorization": "Bearer " + GROQ_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": PROMPT_SISTEMA}] + historico[-20:],
        "temperature": 0.85,
        "max_tokens": 2048,
        "top_p": 0.9
    }
    try:
        resp = requests.post(GROQ_URL, headers=hdrs, json=payload, timeout=90)
        data = resp.json()
        resposta = data["choices"][0]["message"]["content"]
        historico.append({"role": "assistant", "content": resposta})
        return resposta
    except Exception as e:
        return "Erro ao conectar com a IA: " + str(e)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        content = HTML.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)
    def do_POST(self):
        if self.path != '/chat':
            self.send_response(404)
            self.end_headers()
            return
        try:
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length).decode('utf-8')
            params = urllib.parse.parse_qs(body)
            pergunta = params.get('msg', [''])[0]
            if not pergunta.strip():
                resposta = "Por favor, digite uma mensagem."
            else:
                resposta = perguntar(pergunta)
            out = json.dumps({"resposta": resposta}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(out)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(out)
        except Exception as e:
            erro = json.dumps({"resposta": "Erro interno: " + str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(erro)))
            self.end_headers()
            self.wfile.write(erro)

PORT = int(os.environ.get('PORT', 8080))
print("=" * 45)
print("  IA-AVANCADA v2.0 - QI 200")
print("  Porta:", PORT)
print("  Pronto!")
print("=" * 45)
HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()

 
