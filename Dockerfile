# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY data/ ./data/
COPY src/ ./src/
COPY models/ ./models/

# Expose port for Flask API
EXPOSE 5000

# Set Python path
ENV PYTHONPATH=/app

# Default command runs the API
CMD ["python", "src/api.py"]
