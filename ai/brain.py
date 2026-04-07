import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.db import get_connection

class Brain:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.threshold = 0.5
        self.patterns = []
        self.responses = []
        self.ids = []
        self.refresh_knowledge()

    def refresh_knowledge(self):
        """Busca os padrões do banco PostgreSQL (Colunas em Inglês)"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            # Selecionando as colunas que criamos agora em inglês
            cur.execute("SELECT id, user_input, ai_response FROM patterns")
            rows = cur.fetchall()
            if rows:
                self.ids = [r[0] for r in rows]
                self.patterns = [r[1] for r in rows]
                self.responses = [r[2] for r in rows]
                self.vectorizer.fit(self.patterns)
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao carregar conhecimento: {e}")

    def respond(self, text):
        if not self.patterns:
            return {"known": False, "confidence": 0.0, "response": None, "pattern_id": None}

        user_vec = self.vectorizer.transform([text])
        proto_vecs = self.vectorizer.transform(self.patterns)
        similarities = cosine_similarity(user_vec, proto_vecs).flatten()
        
        idx = np.argmax(similarities)
        confidence = similarities[idx]

        if confidence >= self.threshold:
            return {
                "known": True,
                "confidence": float(confidence),
                "response": self.responses[idx],
                "pattern_id": self.ids[idx]
            }
        
        return {"known": False, "confidence": float(confidence), "response": None, "pattern_id": None}

    def learn(self, text, response):
        """Insere novo padrão no banco Loke e atualiza o vetor"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO patterns (user_input, ai_response) VALUES (%s, %s) RETURNING id",
            (text, response)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        self.refresh_knowledge()
        return new_id

    def stats(self):
        return {"total_patterns": len(self.patterns), "ready": len(self.patterns) > 0}