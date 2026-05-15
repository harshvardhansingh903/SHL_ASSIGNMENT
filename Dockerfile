FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY shl_recommender.py .
COPY api_server.py .
COPY stack_generator.py .
COPY semantic_role_clustering.py .
COPY catalog_relationships.py .
COPY refinement_handler.py .
COPY shl_product_catalog_clean.json .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run API
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
