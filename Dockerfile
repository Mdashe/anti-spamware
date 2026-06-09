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

# Download NLTK resources required by preprocess.py
RUN python -m nltk.downloader stopwords wordnet

# Copy project files into the container
COPY . /app

# Set Python path
ENV PYTHONPATH=/app

# Expose a port if you later add an API server
EXPOSE 5000

# Default command runs the training pipeline
CMD ["python", "pipeline.py"]
