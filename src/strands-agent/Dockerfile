# Use ARM64 Python base image for AWS Bedrock Agent Core
FROM --platform=linux/arm64 python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py .
COPY config.py .
COPY entrypoint.py .

# Expose port 8080 (required by Agent Core)
EXPOSE 8080

# Run with OpenTelemetry auto-instrumentation for observability
CMD ["opentelemetry-instrument", "uvicorn", "entrypoint:app", "--host", "0.0.0.0", "--port", "8080"]
