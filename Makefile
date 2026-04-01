.PHONY: up down logs restart ps

up:
	@echo "Starting all Docker containers..."
	docker compose up -d

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