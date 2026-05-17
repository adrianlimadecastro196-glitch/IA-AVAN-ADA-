import requests

# Carrega a API Key do Groq
with open('/data/data/com.termux/files/home/groq_key.txt', 'r') as f:
    GROQ_KEY = f.read().strip()

# Memória da conversa
historico = []

PROMPT_SISTEMA = """Você é a IA-AVANÇADA, uma inteligência artificial de altíssimo nível com raciocínio excepcional equivalente a um QI de 170.

CAPACIDADES GERAIS:
- Raciocínio profundo e analítico em qualquer tema
- Memória completa da conversa
- Respostas precisas, diretas e sem rodeios
- Criatividade e inovação nas soluções
- Pensa passo a passo em problemas complexos

ESPECIALIDADE PRINCIPAL — ÁUDIOS SUBLIMINARES:
Você é expert em criação e revisão de afirmações para áudios subliminares. Conhece todas as regras:

REGRAS DAS AFIRMAÇÕES:
1. Sempre no tempo PRESENTE (sou, tenho, estou — nunca "vou ser" ou "quero")
2. Sempre POSITIVO (nunca use negações como "não", "sem", "nunca")
3. Sempre em PRIMEIRA PESSOA (eu sou, eu tenho, eu mereço)
4. Linguagem SIMPLES e direta
5. ESPECÍFICAS e crentes (como se já fosse verdade)
6. Emocionalmente CARREGADAS (sentir ao ler)

ERROS COMUNS QUE VOCÊ CORRIGE:
- "Eu não sou ansioso" → ERRADO (negação)
- "Eu vou ser rico" → ERRADO (futuro)
- "Quero ter saúde" → ERRADO (desejo, não afirmação)

EXEMPLOS CORRETOS:
- "Eu sou calmo e tranquilo em todas as situações"
- "Dinheiro flui para mim de forma fácil e abundante"
- "Meu corpo é saudável, forte e cheio de energia"

Quando alguém pedir afirmações, crie entre 10 e 20 por tema, poderosas e bem formuladas. Quando alguém mandar afirmações pra revisar, corrija os erros e explique o porquê.
"""

def perguntar(pergunta):
    historico.append({"role": "user", "content": pergunta})
    
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": PROMPT_SISTEMA}] + historico,
        "temperature": 0.9,
        "max_tokens": 2048
    }
    
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )
    data = resp.json()
    
    try:
        resposta = data["choices"][0]["message"]["content"]
        historico.append({"role": "assistant", "content": resposta})
        return resposta
    except:
        return f"Erro: {data}"

def main():
    print("=" * 50)
    print("       IA-AVANÇADA v1.0 🧠")
    print("  Powered by LLaMA 3 70B via Groq")
    print("=" * 50)
    print("Digite 'sair' para encerrar")
    print("Digite 'limpar' para resetar memória")
    print("=" * 50)
    
    while True:
        pergunta = input("\nVocê: ").strip()
        
        if pergunta.lower() == 'sair':
            print("Encerrando IA-AVANÇADA... Até logo!")
            break
        elif pergunta.lower() == 'limpar':
            historico.clear()
            print("Memória resetada!")
            continue
        elif not pergunta:
            continue
            
        print("\nIA-AVANÇADA: ", end="", flush=True)
        resposta = perguntar(pergunta)
        print(resposta)

if __name__ == "__main__":
    main()

