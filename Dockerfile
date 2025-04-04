# Stage 1: Builder
FROM python:3.9-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies: gcc, libpq-dev (provides pg_config) and netcat-openbsd
RUN apt-get update && \
    apt-get install -y gcc libpq-dev netcat-openbsd ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app/

# Stage 2: Production (runtime) stage
FROM python:3.9-slim

# Install runtime dependencies, including libpq5 for psycopg2 to work
RUN apt-get update && \
    apt-get install -y netcat-openbsd libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and setup app directory
RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app
WORKDIR /app

# Copy dependencies and app code from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /app/ /app/
USER appuser

# Expose the port for the Django app
EXPOSE 8000

# Start the application: run migrations and launch the development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
