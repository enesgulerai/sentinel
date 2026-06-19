CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS transactions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    risk_score DECIMAL(5, 4),
    behavior_embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_embedding_hnsw ON transactions USING hnsw (behavior_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
