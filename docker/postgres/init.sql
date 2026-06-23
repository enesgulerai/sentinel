-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- Core Tables
CREATE TABLE IF NOT EXISTS transactions (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_id      VARCHAR(255) UNIQUE NOT NULL,
    user_id             VARCHAR(255) NOT NULL,
    amount              DECIMAL(10, 2) NOT NULL,
    risk_score          DECIMAL(5, 4),
    behavior_embedding  VECTOR(384),
    created_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_transactions_embedding_hnsw
    ON transactions
    USING hnsw (behavior_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id
    ON transactions(user_id);

CREATE INDEX IF NOT EXISTS idx_transactions_created_at
    ON transactions USING brin(created_at);
