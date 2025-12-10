# Docker Build Summary

## What Happens During `docker build`

When you run `docker build -t ai-interns .`, the following happens automatically:

### 1. Base Image Setup (1-2 minutes)
- Downloads Python 3.11 slim image
- Sets up working directory `/app`

### 2. System Dependencies (2-3 minutes)
Installs required system packages:
- `gcc`, `g++`, `make` - Compilation tools
- `libffi-dev`, `libssl-dev` - SSL/crypto libraries
- `git`, `curl` - Version control and downloads

### 3. Python Dependencies (5-10 minutes)
Installs from `requirements.txt`:
- **Web Framework**: Flask, Werkzeug
- **AI/ML**: anthropic, openai, langchain, sentence-transformers
- **Vector DBs**: chromadb, pymilvus, milvus-lite
- **Data Processing**: pandas, torch, openpyxl
- **Cloud**: google-cloud-storage
- **Utilities**: python-dotenv, requests, pdfplumber

### 4. Application Files
Copies entire `Internal-Projects` directory to `/app`

### 5. Vector Database Initialization (5-10 minutes) ⭐
**This is the key automated step that sets up your RAG systems:**

#### Zebra Project ChromaDB (~2-3 minutes)
- **Location**: `/app/Zebra Project/chroma_db/`
- **Data Source**: 32 JSON printer specification files in `output/`
- **Process**:
  1. Reads all JSON files from `Zebra Project/output/`
  2. Extracts printer specifications and metadata
  3. Generates embeddings using SentenceTransformer (all-MiniLM-L6-v2)
  4. Stores in ChromaDB for semantic search
- **Result**: RAG-ready printer spec database with ~100+ document chunks

#### GEN AI Agent Milvus (~3-7 minutes)
- **Location**: `/app/GEN AI Agent/Archive/milvus_edelivery.db`
- **Data Source**: `eDelivery_AIeDelivery_Database_V1.xlsx`
- **Process**:
  1. Loads Excel file (supports GCS buckets too)
  2. Extracts content from all sheets
  3. Generates embeddings for semantic search
  4. Creates two collections:
     - **Structure DB**: Sheet/column metadata
     - **Content DB**: Row-level content with embeddings
- **Result**: Fully indexed Excel database ready for semantic queries

### 6. Final Setup
- Creates database directories
- Sets environment variables
- Configures health check endpoint
- Sets default command to run AI-Interns Flask app

## Total Build Time

| Stage | First Build | Subsequent Builds |
|-------|-------------|-------------------|
| Base Image | 1-2 min | cached |
| System Deps | 2-3 min | cached |
| Python Deps | 5-10 min | cached |
| Vector DBs | 5-10 min | cached* |
| **Total** | **15-25 min** | **2-5 min** |

*Vector DBs are only rebuilt if data files change

## What You Get

After a successful build:

```bash
docker images | grep ai-interns
# ai-interns    latest    abc123    20 mins ago    3.5GB
```

The image includes:
- ✅ Flask web application (AI-Interns)
- ✅ Zebra Project ChromaDB (32 printer specs, ready for RAG)
- ✅ GEN AI Agent Milvus (Excel data, ready for semantic search)
- ✅ All Python dependencies
- ✅ ML models (SentenceTransformers)

## Verify Initialization

Check if vector databases were initialized successfully:

```bash
# Check build logs for success messages
docker build -t ai-interns . 2>&1 | grep "✅"

# You should see:
# ✅ Zebra ChromaDB initialized successfully!
# ✅ GEN AI Milvus initialized successfully!
```

Or test the built image:

```bash
# Check if databases exist
docker run --rm ai-interns python -c "
import os
print('Zebra ChromaDB exists:', os.path.exists('/app/Zebra Project/chroma_db'))
print('GEN AI Milvus exists:', os.path.exists('/app/GEN AI Agent/Archive/milvus_edelivery.db'))
"
```

## Troubleshooting

### Vector DB warnings during build
If you see warnings like `⚠️ No JSON files found` or `⚠️ Excel file not found`:
- The build will continue but vector DBs will be empty
- You can populate them later using GCS or manual initialization
- The Flask app will still work

### Build fails during vector DB initialization
The Dockerfile uses `|| echo "Warning..."` to continue even if initialization fails:
```dockerfile
RUN python init_vector_dbs.py || echo "Warning: Vector DB initialization had issues, continuing..."
```

This ensures the Docker build completes even if:
- Data files are missing
- Embeddings take too long
- Memory issues occur

You can always initialize manually later.

## Manual Vector DB Initialization

If you need to reinitialize vector databases after build:

```bash
# Enter running container
docker exec -it ai-interns-app /bin/bash

# Run initialization script
python /app/init_vector_dbs.py
```

## Cloud Deployment (GCS)

For Cloud Run deployment with GCS:

1. Set environment variables:
```bash
USE_GCS=true
GCS_BUCKET_NAME=your-bucket-name
GCS_FILE_PATH=path/to/excel/file.xlsx
```

2. Use Workload Identity or service account key
3. Build and deploy - will read from GCS during initialization

See [GCS_SETUP.md](GEN%20AI%20Agent/Archive/GCS_SETUP.md) for details.
