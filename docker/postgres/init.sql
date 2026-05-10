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
