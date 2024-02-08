# Makefile

# Name of the web service in docker-compose
SERVICE_NAME := web

# Lint command
lint:
	docker-compose exec $(SERVICE_NAME) python -m black .
	docker-compose exec $(SERVICE_NAME) python -m flake8 --ignore=E501,F405,W503,E231
	docker-compose exec $(SERVICE_NAME) pylint django_template apps tests

# Test command with coverage
test:
	docker-compose exec $(SERVICE_NAME) pytest -n auto --cov=apps --cov-report=html:.app_coverage --cov-report=term

# Shell command
shell:
	docker-compose exec $(SERVICE_NAME) python manage.py shell_plus
