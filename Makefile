.PHONY: up down test

up:
	@echo "Starting all Docker containers..."
	docker compose up -d
	@echo "------------------------------------------------------"
	@echo "System is UP and running! Access the services at:"
	@echo "------------------------------------------------------"
	@echo "UI (Streamlit)      : http://localhost:8501"
	@echo "API Gateway (Docs)  : http://localhost:8000/docs"
	@echo "Redpanda Console    : http://localhost:8080"
	@echo "------------------------------------------------------"

down:
	@echo "Stopping and removing all Docker containers..."
	docker compose down

test:
	@echo "Running all tests with coverage report..."
	python -m pytest tests/ --cov=src --cov-report=term-missing
