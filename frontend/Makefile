.PHONY: help install test test-unit test-integration test-performance coverage lint format clean migrate makemigrations run-dev run-prod deploy

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements/local.txt

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest -m unit

test-integration: ## Run integration tests only
	pytest -m integration

test-performance: ## Run performance tests only
	pytest -m performance

test-api: ## Run API tests only
	pytest -m api

coverage: ## Run tests with coverage report
	pytest --cov=scoringengine --cov=api --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 scoringengine/ api/ tests/
	black --check scoringengine/ api/ tests/
	isort --check-only scoringengine/ api/ tests/

format: ## Format code
	black scoringengine/ api/ tests/
	isort scoringengine/ api/ tests/

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf logs/

migrate: ## Run database migrations
	python manage.py migrate

makemigrations: ## Create new migrations
	python manage.py makemigrations

run-dev: ## Run development server
	python manage.py runserver

run-prod: ## Run production server
	gunicorn hfcscoringengine.wsgi:application --bind 0.0.0.0:8000 --workers 4

deploy: ## Deploy to production
	git push origin main

test-db: ## Test database connection
	python manage.py check --database default

create-superuser: ## Create a superuser
	python manage.py createsuperuser

collect-static: ## Collect static files
	python manage.py collectstatic --noinput

load-fixtures: ## Load test fixtures
	python manage.py loaddata fixtures/*.json

dump-fixtures: ## Dump current data as fixtures
	python manage.py dumpdata --indent 2 > fixtures/current_data.json

backup-db: ## Backup database
	python manage.py dumpdata --indent 2 > backup_$(shell date +%Y%m%d_%H%M%S).json

restore-db: ## Restore database from backup
	python manage.py loaddata backup_*.json

monitor-logs: ## Monitor application logs
	tail -f logs/django.log

monitor-errors: ## Monitor error logs
	tail -f logs/error.log

health-check: ## Check application health
	curl -f http://localhost:8000/health/ || echo "Health check failed"

performance-test: ## Run performance tests
	pytest tests/test_performance.py -v

load-test: ## Run load tests (requires locust)
	locust -f tests/locustfile.py --host=http://localhost:8000

security-check: ## Run security checks
	bandit -r scoringengine/ api/
	safety check

docker-build: ## Build Docker image
	docker build -t hfc-scoring-engine .

docker-run: ## Run Docker container
	docker run -p 8000:8000 hfc-scoring-engine

docker-compose-up: ## Start services with Docker Compose
	docker-compose up -d

docker-compose-down: ## Stop services with Docker Compose
	docker-compose down

setup-dev: install migrate create-superuser ## Setup development environment

setup-test: install migrate ## Setup test environment

ci: lint test coverage ## Run CI pipeline
