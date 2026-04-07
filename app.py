import os
import psycopg2
from flask import Flask, request, jsonify, render_template
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (local) ou do Railway (produção)
load_dotenv()
app = Flask(__name__)

# Configuração da conexão com o Postgres
def get_db_connection():
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError("Variável DATABASE_URL não encontrada no ambiente!")
    return psycopg2.connect(url)

# 1. ROTA PRINCIPAL: Carrega o Painel de Controle (HTML)
@app.route('/')
def index():
    return render_template('index.html')

# 2. ROTA DO CHAT: Onde a mágica acontece
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    user_text = data.get('message', '').strip()
    
    # --- MODO DE APRENDIZADO DIRETO ---
    # Se o usuário digitar algo como "vgv = Valor Geral de Vendas"
    if "=" in user_text:
        try:
            pergunta, resposta = user_text.split("=", 1)
            conn = get_db_connection()
            cur = conn.cursor()
            
            query = "INSERT INTO patterns (user_input, ai_response) VALUES (%s, %s)"
            cur.execute(query, (pergunta.strip().lower(), resposta.strip()))
            
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({
                "response": f"✅ Padrão memorizado: Quando disserem '{pergunta.strip()}', eu responderei isso!",
                "id": None
            })
        except Exception as e:
            return jsonify({"response": f"❌ Erro ao memorizar no banco: {str(e)}"})

    # --- BUSCA NORMAL NO BANCO ---
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Busca por similaridade (ILIKE)
        cur.execute("SELECT id, ai_response FROM patterns WHERE user_input ILIKE %s LIMIT 1", (f'%{user_text.lower()}%',))
        row = cur.fetchone()
        
        if row:
            response_text = row['ai_response']
            response_id = row['id']
        else:
            response_text = "Ainda não tenho um padrão para isso. Me ensine usando: pergunta = resposta"
            response_id = None
            
        cur.close()
        conn.close()
        return jsonify({"response": response_text, "id": response_id})
    except Exception as e:
        return jsonify({"response": f"⚠️ Erro de conexão: {str(e)}"}), 500

# 3. ROTA DE ESTATÍSTICAS: Para o contador lateral "Conhecimento Ativo"
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

# 4. ROTA DE ATUALIZAÇÃO: Para o botão "Corrigir" da interface
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
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 5. ROTA DE CONTRIBUIÇÃO (Compatibilidade com PowerShell)
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
        return jsonify({"status": "sucesso", "id": pattern_id, "mensagem": "Gravado no Postgres de Betim!"}), 201
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == '__main__':
    # O Railway define a porta automaticamente na variável PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)