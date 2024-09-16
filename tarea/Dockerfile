# Usamos una imagen de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los scripts al directorio de trabajo /app
COPY . /app/
COPY dns_server.py /app/

# Instalar supervisor, procps, curl, redis-tools, net-tools, iproute2, y dnsutils (para dig)
RUN apt-get update && \
    apt-get install -y supervisor procps curl redis-tools net-tools iproute2 dnsutils && \
    apt-get clean


# Crear el directorio para los logs
RUN mkdir -p /app/logs

# Copiar el archivo de configuración de supervisord
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Dar permisos de ejecución al script wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Exponer los puertos para FastAPI y gRPC
EXPOSE 8000
EXPOSE 50051

# Iniciar supervisord
CMD ["/usr/bin/supervisord"]

