FROM python:3.12-slim

ARG MQTT_BROKER
ARG MQTT_TOPIC
ARG MQTT_USER
ARG MQTT_PASSWORD

ENV MQTT_BROKER=${MQTT_BROKER}
ENV MQTT_TOPIC=${MQTT_TOPIC}
ENV MQTT_USER=${MQTT_USER}
ENV MQTT_PASSWORD=${MQTT_PASSWORD}


ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB

ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

WORKDIR /app

# Install required packages to build psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "mqtt.py"]