FROM python:3.12-slim

# Definir a pasta padrão do app
WORKDIR /app

# Instalar dependências necessárias para compilar pacotes (PostgreSQL, etc)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copiar os requerimentos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiar todo o código fonte para dentro do container
COPY . .

# Expor a porta que o Gunicorn vai rodar
EXPOSE 5000

# Variáveis padrão
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Comando para inicializar a aplicação com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
