# Sentinel Test Architecture

This project utilizes a high-performance polyglot monorepo architecture. Our testing suite reflects this by using native testing frameworks for each language ecosystem, fully orchestrated via `Taskfile`.

External infrastructure dependencies (Redis, Redpanda, PostgreSQL) are mocked in-memory using dependency injection. This ensures all unit and integration tests run in milliseconds, completely isolated and deterministic.

## Testing Stack
* **Go (API Gateway):** Native `testing` package, `httptest`, and `redismock`.
* **Rust (Validator):** Native `cargo test` for strict schema and serialization validation.
* **Python (ML Consumer):** `pytest` with `pytest-asyncio` and `AsyncMock` for complex data pipelines.
* **Load Testing:** `oha` (Rust-based, ultra-fast HTTP load generator).

## Prerequisites
Before running the tests, ensure you have the Go and Rust toolchains installed. For the Python ML Consumer tests, you must activate your virtual environment:

* **Windows:** `.venv\Scripts\activate`
* **macOS/Linux:** `source .venv/bin/activate`

---

## Running the Test
To run the Go, Rust, and Python test suites sequentially, use the master orchestration command:
```bash
    task test:all
```
*Note: This task enforces a strict pipeline. If any language's test suite fails, the chain will halt immediately to prevent faulty code from proceeding.*
