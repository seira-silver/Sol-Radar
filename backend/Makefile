# Variables for easy maintenance
PYTHON = ./venv/bin/python3
PIP = ./venv/bin/pip

.PHONY: setup install update migrations migrate deploy run stop

# Initial environment setup (Only run once)
setup:
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Sync dependencies if requirements.txt changed
install:
	$(PIP) install -r requirements.txt

# Quick pull and dependency update for production
pull:
	git pull origin main
	$(PIP) install -r requirements.txt

# Database Migrations (since you have Alembic)
migrate:
	$(PYTHON) -m alembic upgrade head

dev:
	uvicorn app.main:app --reload --port 8000

# PM2 Commands
start:
	pm2 start pm2.config.js

restart:
	pm2 restart jollofboard

stop:
	pm2 stop jollofboard

# The "One Command" Deploy for Production
deploy: pull migrate restart