# Makefile

# Name of the web service in docker-compose
SERVICE_NAME := web

# Lint command
lint:
	docker-compose exec $(SERVICE_NAME) python -m black .
	docker-compose exec $(SERVICE_NAME) python -m flake8 --ignore=E501,F405,W503
	docker-compose exec $(SERVICE_NAME) pylint django_template main users tests

# Test command
test:
	docker-compose exec $(SERVICE_NAME) pytest -n auto --lf

# Shell command
shell:
	docker-compose exec $(SERVICE_NAME) python manage.py shell_plus
