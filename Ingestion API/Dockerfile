# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.12-slim

# non root user
RUN useradd -m appuser
USER appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/ ./src/

# environment variables - need to change 
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379

EXPOSE 8000

# run
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]