# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Internal-Projects directory
COPY . .

# Create directories for databases
RUN mkdir -p /app/AI-Interns \
    && mkdir -p "/app/Zebra Project/chroma_db" \
    && mkdir -p "/app/GEN AI Agent/Archive"

# Initialize vector databases (if data files exist)
# This will set up ChromaDB for Zebra Project and Milvus for GEN AI Agent
RUN python init_vector_dbs.py || echo "Warning: Vector DB initialization had issues, continuing..."

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=AI-Interns/app.py

# Expose port 5001 for AI-Interns Flask app
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001', timeout=5)" || exit 1

# Default command runs AI-Interns app
CMD ["python", "AI-Interns/app.py"]
