FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY auth_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código compartilhado
COPY shared /app/shared

# Copiar código do serviço
COPY auth_service/ .

# Expor porta
EXPOSE 8004

# Comando de execução
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
