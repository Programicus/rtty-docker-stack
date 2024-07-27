FROM nginx:alpine

# Install Python and pip
RUN apk add --no-cache bash python3 python3-dev py3-pip build-base libpq-dev 
# Set working directory
WORKDIR /app

# Copy application files
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

# Copy Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB

ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

# Start Gunicorn and Nginx
CMD ["sh", "-c", "gunicorn -w 4 -b unix:/app/gunicorn.sock app:app & nginx -g 'daemon off;'"]
