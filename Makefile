.PHONY: up down logs restart ps

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

restart:
	@echo "Restarting all Docker containers..."
	docker compose down
	docker compose up -d

logs:
	@echo "Tailing logs for all containers..."
	docker compose logs -f

ps:
	@echo "Showing container status..."
	docker compose ps