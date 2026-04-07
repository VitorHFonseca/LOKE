-- 1. Deletar tabelas antigas
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS patterns CASCADE;

-- 2. Criar tabela de Padrões (Conhecimento)
CREATE TABLE patterns (
    id SERIAL PRIMARY KEY,
    user_input TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Criar tabela de Conversas (Histórico)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id TEXT,
    user_input TEXT,
    ai_response TEXT,
    pattern_id INTEGER REFERENCES patterns(id),
    confidence FLOAT,
    learned_here BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Criar tabela de Feedback
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    pattern_id INTEGER REFERENCES patterns(id),
    rating INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);