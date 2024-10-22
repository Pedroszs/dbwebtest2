FROM python:3.12

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libreoffice \
    libmariadb-dev \
    libmariadb-dev-compat \
    build-essential


# Instalar dependências do Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

WORKDIR /app
COPY . /app


EXPOSE 8000


