import os
import psycopg2
from flask import Flask, request, jsonify
import language_tool_python
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# O Railway fornece a DATABASE_URL automaticamente nos serviços conectados
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    try:
        # sslmode='require' é obrigatório para conexões seguras no Railway/Heroku
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")
        return None

# --- INICIALIZAÇÃO DO CORRETOR (MODO REMOTO PARA ECONOMIZAR MEMÓRIA) ---
# Usar o remote_server impede que o Railway tente baixar 500MB de Java
tool = language_tool_python.LanguageTool('pt-BR', remote_server='https://api.languagetool.org/')

@app.route('/')
def home():
    return {
        "status": "online",
        "servico": "Loke AI",
        "mensagem": "Pronto para processar dados de Betim para o mundo!"
    }

# ROTA DE CHAT (CONSULTA)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Mensagem não fornecida"}), 400
    
    user_message = data['message']
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
        
    cur = conn.cursor()
    
    # Busca inteligente usando ILIKE (ignora maiúsculas/minúsculas)
    cur.execute('SELECT ai_response FROM "Loke".patterns WHERE user_input ILIKE %s LIMIT 1', (f'%{user_message}%',))
    result = cur.fetchone()
    
    cur.close()
    conn.close()

    if result:
        return jsonify({"response": result[0]})
    else:
        return jsonify({"response": "Ainda não tenho essa informação no meu cérebro de dados. Me ensine na rota /contribuir!"})

# ROTA DE CONTRIBUIÇÃO (APRENDIZADO COM CORREÇÃO)
@app.route('/contribuir', methods=['POST'])
def contribuir():
    data = request.get_json()
    pergunta_bruta = data.get('pergunta')
    resposta_bruta = data.get('resposta')

    if not pergunta_bruta or not resposta_bruta:
        return jsonify({"error": "Pergunta e resposta são obrigatórias"}), 400

    # 1. Correção de Português Automática via API Remota
    try:
        pergunta_corrigida = tool.correct(pergunta_bruta)
        resposta_corrigida = tool.correct(resposta_bruta)
    except:
        # Fallback caso a API de correção esteja fora do ar
        pergunta_corrigida = pergunta_bruta
        resposta_corrigida = resposta_bruta

    # 2. Persistência no PostgreSQL
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro de banco de dados"}), 500
        
    try:
        cur = conn.cursor()
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
            "status": "sucesso",
            "pergunta_salva": pergunta_corrigida,
            "resposta_salva": resposta_corrigida,
            "nota": "O texto foi corrigido automaticamente antes de ser salvo."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # O Railway define a porta dinamicamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)