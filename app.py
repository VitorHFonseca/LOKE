import os
import psycopg2
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Conexão com o Banco de Dados
def get_db_connection():
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError("Variável DATABASE_URL não encontrada!")
    return psycopg2.connect(url)

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "servico": "Loke AI",
        "mensagem": "Sistema estabilizado e sem Java!"
    })

@app.route('/contribuir', methods=['POST'])
def contribuir():
    data = request.json
    # Ajustado para as colunas do seu novo SQL
    user_input = data.get('pergunta')
    ai_response = data.get('resposta')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = "INSERT INTO patterns (user_input, ai_response) VALUES (%s, %s) RETURNING id"
        cur.execute(query, (user_input, ai_response))
        
        pattern_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "sucesso",
            "id": pattern_id,
            "mensagem": "Gravado no Postgres de Betim!"
        }), 201
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)