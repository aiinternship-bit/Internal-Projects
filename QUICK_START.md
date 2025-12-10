# Quick Start Guide

## Prerequisites

1. **Docker Desktop** installed and running
2. **Anthropic API Key** from https://console.anthropic.com/

## Step 1: Navigate to Project Directory

```bash
# In Cloud Shell or your terminal
cd /path/to/Internal-Projects

# Verify you're in the right place
ls Dockerfile
# Should show: Dockerfile
```

## Step 2: Create .env File

```bash
# Copy the example
cp .env.example .env

# Edit with your API key
nano .env
# or
vim .env
```

Add your API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

## Step 3: Build the Docker Image

### For Local Development (Docker Desktop)

```bash
# Build (takes 15-25 minutes first time)
docker build -t ai-interns .

# Watch for success messages:
# ✅ Zebra ChromaDB initialized successfully!
# ✅ GEN AI Milvus initialized successfully!
```

### For Cloud Shell / GCP (Recommended)

**If you get "no space left on device" error in Cloud Shell, use Cloud Build:**

```bash
# Enable Cloud Build API (first time only)
gcloud services enable cloudbuild.googleapis.com

# Submit build to Cloud Build (runs in Google's infrastructure)
gcloud builds submit --config cloudbuild.yaml .

# This takes 15-25 minutes and runs in the cloud with more resources
# You'll see all the vector DB initialization in the build logs
```

**What happens during build:**
- ✓ System dependencies installed
- ✓ Python packages installed (Flask, Anthropic, PyTorch, etc.)
- ✓ **Zebra Project ChromaDB created** (32 printer specs)
- ✓ **GEN AI Agent Milvus created** (Excel embeddings)

## Step 4: Run the Container

### For Local Development

**Option A: Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option B: Docker CLI**
```bash
docker run -d \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd)/AI-Interns/conversations.db:/app/AI-Interns/conversations.db \
  --name ai-interns-app \
  ai-interns
```

### For Cloud Shell / GCP - Deploy to Cloud Run

**After Cloud Build completes, deploy to Cloud Run:**

```bash
# Deploy the built image to Cloud Run
gcloud run deploy ai-interns \
  --image gcr.io/$(gcloud config get-value project)/ai-interns:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-api03-your-key-here \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10

# Get your public URL
gcloud run services describe ai-interns \
  --region us-central1 \
  --format='value(status.url)'
```

**Your app will be live at:** `https://ai-interns-xxxxx-uc.a.run.app`

## Step 5: Access the Application

### Local Development
Open in your browser:
```
http://localhost:5001
```

### Cloud Run Deployment
Use the URL from the deploy command:
```
https://ai-interns-xxxxx-uc.a.run.app
```

## Step 6: Verify Everything Works

```bash
# Check logs
docker logs -f ai-interns-app

# Should see:
# * Running on http://0.0.0.0:5001
```

Test the chatbot:
1. Click on "Archive" or "Z Printer Scout" tile
2. Type a question (e.g., "What printers do you have?")
3. Get AI response with RAG context

## Common Issues

### "failed to read dockerfile"
**Problem:** You're in the wrong directory

**Solution:**
```bash
pwd  # Check where you are
cd /path/to/Internal-Projects  # Navigate to correct location
ls Dockerfile  # Verify Dockerfile exists
```

### "ANTHROPIC_API_KEY not set"
**Problem:** Missing or incorrect .env file

**Solution:**
```bash
# Check if .env exists
ls -la .env

# Verify it contains your key
cat .env | grep ANTHROPIC_API_KEY
```

### Container won't start
**Problem:** Port 5001 already in use

**Solution:**
```bash
# Find what's using the port
lsof -i :5001

# Kill it or use different port
docker run -d -p 8080:5001 ...
```

## Quick Commands Reference

```bash
# View logs
docker logs -f ai-interns-app

# Stop container
docker stop ai-interns-app

# Start container
docker start ai-interns-app

# Remove container
docker rm ai-interns-app

# Rebuild image
docker build --no-cache -t ai-interns .

# Shell into container
docker exec -it ai-interns-app /bin/bash

# Check vector databases
docker run --rm ai-interns python -c "
import os
print('Zebra DB:', os.path.exists('/app/Zebra Project/chroma_db'))
print('GEN AI DB:', os.path.exists('/app/GEN AI Agent/Archive/milvus_edelivery.db'))
"
```

## Next Steps

- ✅ Test all three chatbots (AppDevReport, Archive, Z Printer Scout)
- ✅ Create conversations and verify persistence
- ✅ Test conversation switching and deletion
- ✅ Verify RAG responses include specific data from vector DBs

## For Production (Cloud Run)

```bash
# Tag for GCR
docker tag ai-interns gcr.io/your-project/ai-interns:latest

# Push to registry
docker push gcr.io/your-project/ai-interns:latest

# Deploy to Cloud Run
gcloud run deploy ai-interns \
  --image gcr.io/your-project/ai-interns:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your-key
```

## Need More Help?

- See [BUILD_CHECKLIST.md](BUILD_CHECKLIST.md) for detailed build guide
- See [DOCKER_BUILD_SUMMARY.md](DOCKER_BUILD_SUMMARY.md) for what happens during build
- See [GCS_SETUP.md](GEN%20AI%20Agent/Archive/GCS_SETUP.md) for Cloud Storage setup
