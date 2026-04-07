import os
import psycopg2
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import language_tool_python

load_dotenv()
app = Flask(__name__)
tool = language_tool_python.LanguageTool('pt-BR')

# Conexão com o Banco de Dados (Pega a variável do Railway automaticamente)
def get_db_connection():
    url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(url)
    return conn

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "servico": "Loke AI",
        "mensagem": "Pronto para processar dados de Betim para o mundo!"
    })

@app.route('/contribuir', methods=['POST'])
def contribuir():
    data = request.json
    pergunta_bruta = data.get('pergunta')
    resposta_bruta = data.get('resposta')

    # Correção Gramatical com LanguageTool
    pergunta_corrigida = tool.correct(pergunta_bruta)
    resposta_corrigida = tool.correct(resposta_bruta)

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Salvando na tabela PATTERNS com as colunas novas
        query = "INSERT INTO patterns (user_input, ai_response) VALUES (%s, %s) RETURNING id"
        cur.execute(query, (pergunta_corrigida, resposta_corrigida))
        
        pattern_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "sucesso",
            "id": pattern_id,
            "original": pergunta_bruta,
            "corrigido": pergunta_corrigida
        }), 201
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == '__main__':
    # Porta padrão para o Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)