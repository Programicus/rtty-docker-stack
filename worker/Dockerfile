FROM python:3.12-slim

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

RUN mkdir /pyrtty
COPY pyrtty/requirements.txt /pyrtty/requirements.txt
RUN pip install --break-system-packages -r /pyrtty/requirements.txt

ADD pyrtty /pyrtty
ENV PATH="/pyrtty:${PATH}"

COPY . .

RUN adduser root audio

CMD ["python", "worker.py"]