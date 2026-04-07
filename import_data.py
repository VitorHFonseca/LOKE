import pandas as pd
from database.db import get_connection

def mass_import(file_path):
    """Lê um CSV e injeta no Schema Loke"""
    print(f"Lendo arquivo: {file_path}...")
    
    try:
        # Carrega o CSV (ajuste o separador se necessário, ex: sep=';')
        df = pd.read_csv(file_path)
        
        # O CSV deve ter colunas chamadas 'pergunta' e 'resposta'
        if 'pergunta' not in df.columns or 'resposta' not in df.columns:
            print("Erro: O CSV precisa ter as colunas 'pergunta' e 'resposta'")
            return

        conn = get_connection()
        cur = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            # Inserindo no seu Schema específico
            cur.execute(
                'INSERT INTO "Loke".patterns (user_input, ai_response) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                (row['pergunta'], row['resposta'])
            )
            count += 1
            
        conn.commit()
        cur.close()
        conn.close()
        print(f"✓ Sucesso! {count} novos padrões adicionados ao banco Loke.")
        
    except Exception as e:
        print(f"Erro na importação: {e}")

if __name__ == "__main__":
    # Exemplo de uso: coloque o nome do seu arquivo aqui
    mass_import("dados_treinamento.csv")