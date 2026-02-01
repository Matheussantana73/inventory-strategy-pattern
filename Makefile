.PHONY: help install migrate populate run setup clean test shell venv

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup      - Configura todo o projeto (venv + install + migrate + populate)"
	@echo "  make venv       - Cria o ambiente virtual"
	@echo "  make install    - Instala as dependências do requirements.txt"
	@echo "  make migrate    - Executa as migrações do banco de dados"
	@echo "  make populate   - Popula o banco de dados com dados iniciais"
	@echo "  make run        - Inicia o servidor de desenvolvimento"
	@echo "  make clean      - Remove o banco de dados e arquivos cache"
	@echo "  make test       - Executa os testes"
	@echo "  make shell      - Abre o shell do Django"
	@echo "  make superuser  - Cria um superusuário"

setup: venv install migrate populate
	@echo "✅ Projeto configurado com sucesso!"
	@echo "Execute 'make run' para iniciar o servidor"

venv:
	@echo "🔧 Criando ambiente virtual..."
	python3 -m venv $(VENV)
	@echo "✅ Ambiente virtual criado em ./$(VENV)"

install: venv
	@echo "📦 Instalando dependências..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

migrate:
	@echo "🔄 Executando migrações..."
	$(PYTHON) manage.py makemigrations
	$(PYTHON) manage.py migrate

populate:
	@echo "📝 Populando banco de dados..."
	$(PYTHON) popular_db.py

run:
	@echo "🚀 Iniciando servidor de desenvolvimento..."
	$(PYTHON) manage.py runserver

clean:
	@echo "🧹 Limpando projeto..."
	rm -f db.sqlite3
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Projeto limpo!"

test:
	@echo "🧪 Executando testes..."
	$(PYTHON) manage.py test

shell:
	@echo "🐚 Abrindo shell do Django..."
	$(PYTHON) manage.py shell

superuser:
	@echo "👤 Criando superusuário..."
	$(PYTHON) manage.py createsuperuser
