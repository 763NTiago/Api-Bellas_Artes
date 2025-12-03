# Imagem base leve do Python
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Garante que os logs apareçam imediatamente no console
ENV PYTHONUNBUFFERED=1

# Define diretório de trabalho no container
WORKDIR /app

# Instala dependências do sistema (opcional, caso precise de algo específico para SQLite/Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala dependências do Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o projeto inteiro
COPY . /app/

# Expõe a porta 8000
EXPOSE 8000

# Comando para rodar (usando o servidor de desenvolvimento por enquanto ou gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]