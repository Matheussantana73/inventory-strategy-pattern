FROM python:3.11-slim

WORKDIR /app

# Instalar curl para health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY calculo_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do serviço
COPY calculo_service/ .

# Expor porta
EXPOSE 8003

# Comando de execução
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
