# Multi-stage build: build frontend with Node, then assemble final image with Python + nginx

# Frontend builder
FROM node:18 AS builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ .
RUN npm install --legacy-peer-deps
RUN npm run build

# Final image: Python + nginx
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

# Install nginx and other useful packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy frontend build into nginx html directory
COPY --from=builder /app/frontend/dist /usr/share/nginx/html

# Copy backend source
COPY backend /app/backend

# Install python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy nginx config and startup script
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/start.sh /start.sh
# Normalize line endings to LF in case the file had CRLF on Windows hosts
RUN sed -i 's/\r$//' /start.sh
RUN chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
