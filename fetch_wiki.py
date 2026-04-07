import wikipedia
import psycopg2
from database.db import get_connection
import logging

# Configuração de Idioma (Pode ser 'pt' ou 'en' para dados globais)
wikipedia.set_lang("pt")

logging.basicConfig(level=logging.INFO)

def fetch_and_save_topics():
    # Lista de temas para tornar o Loke um especialista global
    topics = [
        "Economia global", "História do Mundo", "Inteligência Artificial",
        "Exploração espacial", "Geopolítica", "Mercado financeiro",
        "Bitcoin", "Sistema Solar", "Revolução Industrial", "NASA",
        "Tecnologia da informação", "Culinária italiana", "História de Minas Gerais"
    ]

    conn = get_connection()
    if not conn:
        logging.error("❌ Falha na conexão com o Banco de Dados.")
        return

    try:
        cur = conn.cursor()
        
        for topic in topics:
            logging.info(f"🔍 Minerando dados sobre: {topic}...")
            try:
                # Busca o resumo da página
                page = wikipedia.page(topic, auto_suggest=False)
                content = page.summary
                
                # Limpeza básica: remove quebras de linha excessivas
                clean_content = " ".join(content.split())
                
                # INSERT com ON CONFLICT (Evita duplicatas se você rodar o script de novo)
                # Assumindo que sua tabela 'patterns' tem uma constraint UNIQUE na coluna 'user_input'
                query = """
                INSERT INTO "Loke".patterns (user_input, ai_response)
                VALUES (%s, %s)
                ON CONFLICT (user_input) DO UPDATE SET ai_response = EXCLUDED.ai_response;
                """
                
                cur.execute(query, (topic, clean_content))
                logging.info(f"✅ Sucesso: {topic} salvo no Schema 'Loke'.")
                
            except wikipedia.exceptions.DisambiguationError as e:
                logging.warning(f"⚠️ Ambiguidade em '{topic}': {e.options[:3]}")
            except Exception as e:
                logging.error(f"❌ Erro ao processar '{topic}': {e}")

        conn.commit()
        cur.close()
        logging.info("🚀 Pipeline de ingestão finalizado com sucesso!")

    except Exception as e:
        logging.error(f"💥 Erro crítico no banco: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_and_save_topics()