# Stage 1: Builder
FROM python:3.9-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y gcc libpq-dev netcat-openbsd ca-certificates \
    texlive-latex-base texlive-latex-recommended texlive-fonts-recommended texlive-extra-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Stage 2: Runtime
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y netcat-openbsd libpq5 \
    texlive-latex-base texlive-latex-recommended texlive-fonts-recommended texlive-extra-utils \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /app/ /app/

# Copy wait-for-db script
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

USER appuser
EXPOSE 8000

# Use entrypoint to wait for DB before running command
ENTRYPOINT ["/wait-for-db.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

