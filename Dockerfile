# Stage 1: Builder
FROM python:3.9-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && \
    apt-get install -y gcc libpq-dev netcat-openbsd ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Stage 2: Runtime
FROM python:3.9-slim

# Install runtime dependencies including psql client
RUN apt-get update && \
    apt-get install -y netcat-openbsd libpq5 postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy wait-for-db.sh script and make it executable BEFORE switching users
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Create appuser and set up app directory
RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app
WORKDIR /app

# Copy dependencies and app code from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /app/ /app/

USER appuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
