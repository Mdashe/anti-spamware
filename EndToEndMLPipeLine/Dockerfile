FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK resources at BUILD TIME — not at runtime
# Without this, the container crashes on first prediction (no internet in Docker)
RUN python -m nltk.downloader stopwords wordnet punkt omw-1.4

COPY src/ ./src/
COPY api/ ./api/
COPY configs/ ./configs/

EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]