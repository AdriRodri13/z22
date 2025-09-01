# Imagen base
FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Evitar pyc y forzar stdout sin buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema necesarias para psycopg2 y Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Crear carpeta staticfiles para WhiteNoise
RUN mkdir -p /app/staticfiles

# Ejecutar collectstatic para producción
RUN python manage.py collectstatic --noinput

# Exponer puerto (Railway lo inyecta dinámicamente, pero Gunicorn escucha en 0.0.0.0:8000 por defecto)
EXPOSE 8000

# Comando por defecto: Gunicorn
CMD ["gunicorn", "z22.wsgi:application", "--bind", "0.0.0.0:8000", "--log-file", "-"]
