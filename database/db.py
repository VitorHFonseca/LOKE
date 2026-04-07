import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        # IMPORTANTE: Definir o schema para a sessão inteira
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "Loke"')
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco no schema Loke: {e}")
        return None

def test_connection():
    try:
        conn = get_connection()
        conn.close()
        return True
    except:
        return False

def seed_from_json():
    """Popula o banco com as colunas em INGLÊS"""
    print("Iniciando o processo de seed no banco Loke...")
    padroes = [
        ("Olá", "Olá! Eu sou o Loke. Como posso te ajudar hoje?"),
        ("Quem é você?", "Eu sou uma inteligência artificial que aprende com as nossas conversas."),
        ("Como você funciona?", "Eu utilizo PLN e PostgreSQL para evoluir.")
    ]
    try:
        conn = get_connection()
        cur = conn.cursor()
        for u_input, a_res in padroes:
            cur.execute(
                "INSERT INTO patterns (user_input, ai_response) VALUES (%s, %s)",
                (u_input, a_res)
            )
        conn.commit()
        cur.close()
        conn.close()
        print("✓ Seed em inglês finalizado com sucesso!")
    except Exception as e:
        print(f"Erro no seed: {e}")

def save_conversation(user_input, ai_response, session_id, pattern_id, confidence, learned_here):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO conversations (user_input, ai_response, session_id, pattern_id, confidence, learned_here)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_input, ai_response, session_id, pattern_id, confidence, learned_here))
    conn.commit()
    cur.close()
    conn.close()

def get_recent_conversations(limit=20):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM conversations ORDER BY created_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def save_feedback(conversation_id, rating, pattern_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feedback (conversation_id, rating, pattern_id)
        VALUES (%s, %s, %s)
    """, (conversation_id, rating, pattern_id))
    conn.commit()
    cur.close()
    conn.close()