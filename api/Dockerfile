FROM python:3.11-slim
WORKDIR /app
COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY embeddings/ ./embeddings/
COPY rag/ ./rag/
COPY api/ ./api/
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
