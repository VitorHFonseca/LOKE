import os
import psycopg2
from flask import Flask, request, jsonify, render_template
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Conexão com o Banco de Dados
def get_db_connection():
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError("Variável DATABASE_URL não encontrada!")
    return psycopg2.connect(url)

# ROTA 1: Carrega a Interface Bonitona
@app.route('/')
def index():
    return render_template('index.html')

# ROTA 2: A lógica do Chatbot (Busca no banco)
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    user_text = data.get('message', '').lower()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Busca um padrão que combine com o que o usuário digitou
        cur.execute("SELECT id, ai_response FROM patterns WHERE user_input ILIKE %s LIMIT 1", (f'%{user_text}%',))
        row = cur.fetchone()
        
        if row:
            response_text = row['ai_response']
            response_id = row['id']
        else:
            response_text = "Ainda não tenho um padrão para isso. Quer cadastrar no banco?"
            response_id = None
            
        cur.close()
        conn.close()
        return jsonify({"response": response_text, "id": response_id})
    except Exception as e:
        return jsonify({"response": f"Erro no banco: {str(e)}"}), 500

# ROTA 3: Pega o total de padrões para o Sidebar
@app.route('/stats')
def stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM patterns")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"total_patterns": count})
    except:
        return jsonify({"total_patterns": 0})

# ROTA 4: Permite a edição direto no Chat (O botão "Corrigir")
@app.route('/update_pattern', methods=['POST'])
def update_pattern():
    data = request.json
    p_id = data.get('id')
    new_res = data.get('new_response')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE patterns SET ai_response = %s WHERE id = %s", (new_res, p_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except:
        return jsonify({"success": False}), 500

# ROTA 5: Mantém a compatibilidade com seu comando PowerShell
@app.route('/contribuir', methods=['POST'])
def contribuir():
    data = request.json
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
        return jsonify({"status": "sucesso", "id": pattern_id}), 201
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)