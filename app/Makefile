# Makefile for LLM Search Backend with Database Support

.PHONY: help setup install dev test lint format clean docker-build docker-up docker-down docker-logs backup

# Default target
help:
	@echo "LLM Search Backend with Database - Available Commands:"
	@echo ""
	@echo "Setup & Development:"
	@echo "  setup          - Setup development environment"
	@echo "  install        - Install Python dependencies"
	@echo "  dev            - Run development server"
	@echo "  test           - Run tests"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code with black and isort"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-up      - Start all services"
	@echo "  docker-down    - Stop all services"
	@echo "  docker-logs    - View logs"
	@echo "  docker-clean   - Clean Docker resources"
	@echo ""
	@echo "Database Commands:"
	@echo "  db-init        - Initialize database with tables"
	@echo "  db-migrate     - Run database migrations"
	@echo "  db-upgrade     - Upgrade database to latest migration"
	@echo "  db-downgrade   - Downgrade database (use: make db-downgrade REV=<revision>)"
	@echo "  db-seed        - Seed database with test data"
	@echo "  db-reset       - Reset database (WARNING: destroys all data)"
	@echo "  db-backup      - Create database backup"
	@echo "  db-restore     - Restore database from backup"
	@echo "  db-shell       - Connect to database shell"
	@echo "  db-status      - Show database migration status"
	@echo ""
	@echo "Services Management:"
	@echo "  services-up    - Start support services (DB, Redis, Ollama)"
	@echo "  services-down  - Stop support services"
	@echo "  services-logs  - View service logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean          - Clean temporary files"
	@echo "  clean-cache    - Clear application cache"
	@echo "  clean-db       - Clean old database records"

# Setup development environment
setup:
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  # Linux/Mac"
	@echo "  venv\\Scripts\\activate     # Windows"
	@echo "Then run: make install"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Install development dependencies
install-dev: install
	pip install pytest pytest-asyncio pytest-cov pytest-mock
	pip install black isort flake8 mypy bandit
	@echo "Development dependencies installed!"

# Run development server
dev:
	@echo "Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run development server with auto-reload
dev-watch:
	@echo "Starting development server with file watching..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --reload-dir app

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run specific test file
test-file:
	@echo "Running specific test file..."
	@read -p "Enter test file path: " filepath; \
	pytest $$filepath -v

# Test database operations
test-db:
	@echo "Running database tests..."
	pytest tests/database/ -v

# Run linting
lint:
	@echo "Running linting..."
	flake8 app tests --max-line-length=100 --ignore=E203,W503
	mypy app --ignore-missing-imports
	bandit -r app -f json -o security-report.json

# Format code
format:
	@echo "Formatting code..."
	black app tests --line-length=100
	isort app tests --profile=black

# Check code style
check-style:
	@echo "Checking code style..."
	black app tests --check --line-length=100
	isort app tests --check-only --profile=black

# Docker commands
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting all services..."
	docker-compose up -d

docker-up-with-tools:
	@echo "Starting all services with management tools..."
	docker-compose --profile tools up -d

docker-up-with-monitoring:
	@echo "Starting all services with monitoring..."
	docker-compose --profile tools --profile monitoring up -d

docker-down:
	@echo "Stopping all services..."
	docker-compose down

docker-logs:
	@echo "Viewing logs..."
	docker-compose logs -f

docker-logs-api:
	@echo "Viewing API logs..."
	docker-compose logs -f api

docker-logs-db:
	@echo "Viewing database logs..."
	docker-compose logs -f db

docker-restart:
	@echo "Restarting services..."
	docker-compose restart

docker-clean:
	@echo "Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f

# Database commands
db-init:
	@echo "Initializing database..."
	python scripts/init_database.py

db-init-docker:
	@echo "Initializing database in Docker..."
	docker-compose --profile init up db-init

db-migrate:
	@echo "Creating new database migration..."
	@read -p "Enter migration message: " message; \
	python scripts/create_alembic_migration.py --create "$$message"

db-upgrade:
	@echo "Upgrading database to latest migration..."
	python scripts/create_alembic_migration.py --upgrade

db-downgrade:
	@echo "Downgrading database..."
	python scripts/create_alembic_migration.py --downgrade $(REV)

db-status:
	@echo "Checking database migration status..."
	python scripts/create_alembic_migration.py --current
	python scripts/create_alembic_migration.py --history

db-seed:
	@echo "Seeding database with test data..."
	python scripts/seed_database.py

db-seed-docker:
	@echo "Seeding database in Docker..."
	docker-compose --profile seed up db-seed

db-reset:
	@echo "⚠️  WARNING: This will destroy ALL data!"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		python scripts/init_database.py --reset; \
	else \
		echo "Database reset cancelled."; \
	fi

db-backup:
	@echo "Creating database backup..."
	mkdir -p backups
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose exec -T db pg_dump -U searchuser searchdb > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql; \
	else \
		pg_dump -h localhost -U searchuser searchdb > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql; \
	fi
	@echo "Backup created in backups/ directory"

db-restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file path: " filepath; \
	if [ -f "$$filepath" ]; then \
		if command -v docker-compose >/dev/null 2>&1; then \
			docker-compose exec -T db psql -U searchuser -d searchdb < "$$filepath"; \
		else \
			psql -h localhost -U searchuser -d searchdb < "$$filepath"; \
		fi; \
		echo "Database restored from $$filepath"; \
	else \
		echo "Backup file not found: $$filepath"; \
	fi

db-shell:
	@echo "Connecting to database shell..."
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose exec db psql -U searchuser -d searchdb; \
	else \
		psql -h localhost -U searchuser searchdb; \
	fi

db-clean:
	@echo "Cleaning old database records..."
	@read -p "Delete records older than how many days? (default: 30): " days; \
	days=$${days:-30}; \
	python -c "import asyncio; from app.api.endpoints.admin import cleanup_database; print('Cleaning records older than $$days days...')"

# Services management
services-up:
	@echo "Starting support services (DB, Redis, Ollama)..."
	docker-compose up -d db redis ollama

services-down:
	@echo "Stopping support services..."
	docker-compose stop db redis ollama

services-logs:
	@echo "Viewing service logs..."
	docker-compose logs -f db redis ollama

services-restart:
	@echo "Restarting support services..."
	docker-compose restart db redis ollama

# Development utilities
install-ollama:
	@echo "Installing Ollama locally..."
	curl -fsSL https://ollama.ai/install.sh | sh
	ollama pull llama2:7b

check-apis:
	@echo "Checking API connections..."
	python scripts/check_api_keys.py

check-db:
	@echo "Checking database connection..."
	python -c "import asyncio; from app.database.connection import db_manager; asyncio.run(db_manager.initialize()); print('Database connection: OK')"

# Monitoring and maintenance
logs:
	@echo "Viewing application logs..."
	tail -f logs/app.log

monitor:
	@echo "Starting monitoring dashboard..."
	@echo "Open http://localhost:8080 for pgAdmin"
	@echo "Open http://localhost:8081 for Redis Commander"
	@echo "Open http://localhost:3000 for Grafana (if monitoring profile is up)"

health:
	@echo "Checking application health..."
	curl -s http://localhost:8000/health/detailed | jq '.' || curl -s http://localhost:8000/health/detailed

stats:
	@echo "Getting application statistics..."
	curl -s http://localhost:8000/api/v1/search/stats | jq '.' || curl -s http://localhost:8000/api/v1/search/stats

# Cache management
clean-cache:
	@echo "Clearing application cache..."
	curl -X POST http://localhost:8000/api/v1/search/clear-cache || echo "Cache clear failed - is the API running?"

clear-redis:
	@echo "Clearing Redis cache..."
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose exec redis redis-cli FLUSHALL; \
	else \
		redis-cli FLUSHALL; \
	fi

# Clean up
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/

# Production deployment
deploy-prod:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.yml --profile production up -d

deploy-staging:
	@echo "Deploying to staging..."
	docker-compose -f docker-compose.yml up -d

# Quick development setup
quick-start:
	@echo "Quick start for development..."
	cp .env.example .env
	@echo "✅ Environment file created (.env)"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your API keys"
	@echo "2. Run: make docker-up"
	@echo "3. Run: make db-init-docker"
	@echo "4. Optional: make db-seed-docker"
	@echo "5. Visit: http://localhost:8000/docs"

quick-start-local:
	@echo "Quick start for local development..."
	cp .env.example .env
	make install-dev
	make services-up
	sleep 10
	make db-init
	@echo ""
	@echo "✅ Local development environment ready!"
	@echo "Run: make dev"

# Security and maintenance
security-check:
	@echo "Running security checks..."
	bandit -r app -f json -o security-report.json
	@echo "Security report generated: security-report.json"

update-deps:
	@echo "Updating dependencies..."
	pip list --outdated
	@echo "Review outdated packages above and update requirements.txt manually"

# Performance testing
perf-test:
	@echo "Running performance tests..."
	@echo "Performance testing not implemented yet"
	@echo "Consider using tools like locust or wrk for load testing"

# Development helpers
create-user:
	@echo "Creating test user..."
	python -c "import asyncio; from scripts.create_test_user import create_user; asyncio.run(create_user())"

sample-request:
	@echo "Making sample search request..."
	curl -X POST http://localhost:8000/api/v1/search \
		-H "Content-Type: application/json" \
		-d '{"query": "artificial intelligence trends", "max_results": 5}' | jq '.'

# Comprehensive setup for new developers
setup-dev-env:
	@echo "Setting up complete development environment..."
	make setup
	@echo "Virtual environment created. Now run:"
	@echo "source venv/bin/activate"
	@echo "make install-dev"
	@echo "make quick-start-local"

# Variables for parameterized commands
DAYS ?= 30
REV ?= -1
ENV ?= development

# Help for specific categories
help-docker:
	@echo "Docker Commands:"
	@echo "  docker-build               - Build all Docker images"
	@echo "  docker-up                  - Start all services"
	@echo "  docker-up-with-tools       - Start with pgAdmin and Redis Commander"
	@echo "  docker-up-with-monitoring  - Start with monitoring stack"
	@echo "  docker-down                - Stop all services"
	@echo "  docker-clean               - Remove all containers and volumes"

help-db:
	@echo "Database Commands:"
	@echo "  db-init                    - Initialize database schema"
	@echo "  db-migrate                 - Create new migration"
	@echo "  db-upgrade                 - Apply pending migrations"
	@echo "  db-downgrade REV=<rev>     - Downgrade to specific revision"
	@echo "  db-seed                    - Add sample data"
	@echo "  db-reset                   - Reset database (destroys data)"
	@echo "  db-backup                  - Create database backup"
	@echo "  db-restore                 - Restore from backup"
	@echo "  db-shell                   - Connect to database"
