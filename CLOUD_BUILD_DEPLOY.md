# Cloud Build & Deploy Guide (Cloud Run)

**Complete guide for deploying AI-Interns to Google Cloud Run using Cloud Build**

---

## Prerequisites

- ✅ Google Cloud Project
- ✅ Cloud Shell access (or gcloud CLI installed)
- ✅ Anthropic API key

---

## Step 1: Set Up Secret Manager (One-Time Setup)

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Create secret with your API key
echo -n "sk-ant-api03-YOUR-ACTUAL-KEY-HERE" | \
  gcloud secrets create anthropickey \
    --data-file=- \
    --replication-policy="automatic"

# Grant Cloud Run access to the secret
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding anthropickey \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "✅ Secret Manager configured!"
```

**Replace `sk-ant-api03-YOUR-ACTUAL-KEY-HERE` with your real Anthropic API key!**

---

## Step 2: Navigate to Project Directory

```bash
cd Internal-Projects

# Verify you're in the right place
ls cloudbuild.yaml Dockerfile
# Should show both files
```

---

## Step 3: Build with Cloud Build

```bash
# Enable Cloud Build API (first time only)
gcloud services enable cloudbuild.googleapis.com

# Submit build (takes 15-25 minutes)
gcloud builds submit --config cloudbuild.yaml .
```

**What happens during build:**
- 🔧 System dependencies installed
- 📦 Python packages installed (Flask, Anthropic, PyTorch, etc.)
- 🗄️ **Zebra Project ChromaDB created** (32 printer specifications)
- 🗄️ **GEN AI Agent Milvus created** (Excel data embeddings)
- 🐳 Docker image pushed to Container Registry

**Watch for these success messages:**
```
✅ Zebra ChromaDB initialized successfully!
✅ GEN AI Milvus initialized successfully!
```

---

## Step 4: Deploy to Cloud Run

```bash
gcloud run deploy ai-interns \
  --image gcr.io/$(gcloud config get-value project)/ai-interns:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --port 8080
```

**Note:** No `--set-env-vars` needed! The app automatically fetches the API key from Secret Manager.

---

## Step 5: Get Your App URL

```bash
gcloud run services describe ai-interns \
  --region us-central1 \
  --format='value(status.url)'
```

Your app will be live at: `https://ai-interns-xxxxxxxxxx-uc.a.run.app`

---

## Step 6: Verify Deployment

```bash
# Check logs
gcloud run services logs read ai-interns --region us-central1 --limit 20
```

**Look for these messages:**
```
📝 Fetching API key from Secret Manager: projects/YOUR-PROJECT/secrets/anthropickey/versions/latest
✅ Successfully retrieved API key from Secret Manager
🚀 Starting Flask app on host 0.0.0.0, port 8080
   PORT environment variable: 8080
```

---

## All-In-One Command

Copy and paste this complete sequence:

```bash
# Navigate to project
cd Internal-Projects

# Enable APIs
gcloud services enable secretmanager.googleapis.com cloudbuild.googleapis.com

# Create secret (replace with your actual key!)
echo -n "sk-ant-api03-YOUR-KEY" | gcloud secrets create anthropickey --data-file=- --replication-policy="automatic"

# Grant access
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding anthropickey \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Build
gcloud builds submit --config cloudbuild.yaml .

# Deploy
gcloud run deploy ai-interns \
  --image gcr.io/$(gcloud config get-value project)/ai-interns:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --port 8080

# Get URL
gcloud run services describe ai-interns --region us-central1 --format='value(status.url)'
```

---

## Troubleshooting

### Build Fails

**Check build logs:**
```bash
gcloud builds list --limit=1
# Note the BUILD_ID
gcloud builds log <BUILD_ID>
```

### Deployment Fails

**Check service logs:**
```bash
gcloud run services logs read ai-interns --region us-central1 --limit 50
```

### Can't Access Secret

**Verify secret exists:**
```bash
gcloud secrets list
gcloud secrets versions access latest --secret="anthropickey"
```

**Re-grant permissions:**
```bash
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding anthropickey \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Update Deployment

To deploy changes:

```bash
# 1. Rebuild
gcloud builds submit --config cloudbuild.yaml .

# 2. Redeploy (Cloud Run auto-uses latest image)
gcloud run deploy ai-interns \
  --image gcr.io/$(gcloud config get-value project)/ai-interns:latest \
  --region us-central1
```

---

## Cost Estimate

- **Cloud Build**: First 120 build-minutes/day FREE, then $0.003/min
- **Cloud Run**: First 2 million requests/month FREE
- **Secret Manager**: $0.06/month per secret
- **Container Registry**: $0.026/GB/month storage

**Typical monthly cost: $1-5** for low-medium traffic

---

## Next Steps

1. ✅ Open your Cloud Run URL in a browser
2. ✅ Test the chatbot with all three projects
3. ✅ Verify conversations are created and saved
4. ✅ Test RAG functionality (ask about printers or data)

**You're live! 🎉**
