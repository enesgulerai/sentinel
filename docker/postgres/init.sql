-- Enable the pgvector extension for ML embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a base table for future fraud detection data
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    risk_score DECIMAL(5, 4),
    behavior_embedding VECTOR(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OPTIMIZATION 1: O(1) Exact Match Lookups for Transaction IDs
-- Ideal for lightning-fast deduplication checks and API lookups.
CREATE INDEX idx_transactions_id_hash ON transactions USING HASH (transaction_id);

-- OPTIMIZATION 2: Approximate Nearest Neighbor (ANN) index for ML Vectors
-- Allows sub-millisecond similarity searches for 384-dimensional behavioral embeddings.
-- m=16 and ef_construction=64 are highly optimized defaults for pgvector.
CREATE INDEX idx_transactions_embedding_hnsw ON transactions USING hnsw (behavior_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
