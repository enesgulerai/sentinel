# Sentinel: Testing Architecture

*Deterministic, polyglot testing suite orchestrated via Taskfile. External dependencies (Redis, Redpanda, PostgreSQL) are strictly mocked in-memory via dependency injection for isolated, millisecond execution.*

## Testing Stack

| Environment | Frameworks & Tooling | Focus Area |
| :--- | :--- | :--- |
| **Go (API)** | `testing`, `httptest`, `redismock` | API routing, state management, HTTP handlers. |
| **Rust (Validator)** | `cargo test` | Strict schema validation, serialization. |
| **Python (Consumer)**| `pytest`, `pytest-asyncio`, `AsyncMock` | Async event pipelines, inference engine mocking. |
| **Load Testing** | `k6` | High-concurrency HTTP stress generation. |

## Execution Lifecycle

The master orchestration command runs all language test suites sequentially. The pipeline enforces a strict **halt-on-failure** policy to prevent faulty code progression.

```bash
# 1. Activate Python virtual environment (Required for ML tests)
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate

# 2. Execute universal test orchestration
task test:all
```
