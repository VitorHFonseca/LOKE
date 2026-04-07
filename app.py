import os
import psycopg2
from flask import Flask, request, jsonify, render_template
import language_tool_python
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (local) ou do Railway (produção)
load_dotenv()

app = Flask(__name__)

# Configuração do Banco de Dados
DATABASE_URL = os.environ.get('DATABASE_URL') # O Railway fornece isso automaticamente

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# Inicializa o Corretor de Português
tool = language_tool_python.LanguageTool('pt-BR')

# --- ROTAS DO LOKE ---

@app.route('/')
def index():
    return "Loke AI está Online! 🚀"

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Busca no seu banco de patterns (usando ILIKE para ser case-insensitive)
    cur.execute('SELECT ai_response FROM "Loke".patterns WHERE user_input ILIKE %s LIMIT 1', (f'%{user_message}%',))
    result = cur.fetchone()
    
    cur.close()
    conn.close()

    if result:
        return jsonify({"response": result[0]})
    else:
        return jsonify({"response": "Ainda não aprendi sobre isso, mas você pode me ensinar na aba de contribuição!"})

@app.route('/contribuir', methods=['POST'])
def contribuir():
    data = request.json
    pergunta_bruta = data.get('pergunta')
    resposta_bruta = data.get('resposta')

    # 1. Corrigir o Português antes de salvar
    pergunta_corrigida = tool.correct(pergunta_bruta)
    resposta_corrigida = tool.correct(resposta_bruta)

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 2. Insert com ON CONFLICT (para não duplicar)
        query = """
            INSERT INTO "Loke".patterns (user_input, ai_response) 
            VALUES (%s, %s)
            ON CONFLICT (user_input) DO UPDATE SET ai_response = EXCLUDED.ai_response
        """
        cur.execute(query, (pergunta_corrigida, resposta_corrigida))
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "Sucesso",
            "mensagem": "Conhecimento armazenado e corrigido!",
            "original": pergunta_bruta,
            "corrigido": pergunta_corrigida
        })
    except Exception as e:
        return jsonify({"status": "Erro", "detalhes": str(e)}), 500

if __name__ == "__main__":
    # O Railway usa a variável PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)