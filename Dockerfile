FROM python:3.11-slim

# Set working directory (Render uses /opt/render/project/src for Python apps)
WORKDIR /app

# Copy entire project
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure catalog file is present
RUN test -f data/shl_product_catalog_clean.json || (echo "ERROR: Catalog file missing" && exit 1)

# Expose port 8000
EXPOSE 8000

# Run the API
CMD ["python", "-m", "uvicorn", "app.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
