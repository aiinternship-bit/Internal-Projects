# Building in Google Cloud Shell

## The "No Space Left on Device" Problem

Cloud Shell has limited space in the home directory (`~/.docker/`), even though the VM has 100GB total disk.

**Error you might see:**
```
ERROR: failed to build: failed to update builder last activity time:
write /home/ai_internship/.docker/buildx/activity/.tmp-default275307361: no space left on device
```

## Solutions

### Solution 1: Clean Docker Build Cache (Try This First)

```bash
# Clean all Docker cache and unused data
docker system prune -a --volumes -f

# Check available space
df -h ~
df -h /tmp
```

### Solution 2: Use Cloud Build Instead of Local Build

Google Cloud Build has much more resources and is recommended for large builds:

```bash
# Submit build to Cloud Build (runs in Google's infrastructure)
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/ai-interns .

# This builds in the cloud with more resources
# Takes 15-25 minutes, you'll see all the vector DB initialization happen
```

**Advantages:**
- ✅ No local disk space issues
- ✅ Faster build (dedicated resources)
- ✅ Automatic push to Container Registry
- ✅ Build logs saved for review

**After Cloud Build completes:**
```bash
# Deploy directly to Cloud Run
gcloud run deploy ai-interns \
  --image gcr.io/$(gcloud config get-value project)/ai-interns \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your-key-here \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

### Solution 3: Use /tmp for Docker Build Cache

If you must build locally in Cloud Shell:

```bash
# Stop Docker daemon
sudo systemctl stop docker

# Move Docker directory to /tmp (more space)
sudo mv /home/ai_internship/.docker /tmp/.docker
sudo ln -s /tmp/.docker /home/ai_internship/.docker

# Start Docker daemon
sudo systemctl start docker

# Now try building again
docker build -t ai-interns .
```

### Solution 4: Build with Reduced Cache

```bash
# Build without using cache (slower but uses less space)
docker build --no-cache -t ai-interns .
```

## Recommended Approach for Cloud Shell

**Use Cloud Build** - it's designed for this:

```bash
# 1. Make sure you're in the right directory
cd /path/to/Internal-Projects
pwd  # Should show Internal-Projects

# 2. Check if .env exists (Cloud Build will need it)
ls .env

# 3. Create cloudbuild.yaml for better control
cat > cloudbuild.yaml <<'EOF'
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ai-interns:latest', '.']
    timeout: 1800s  # 30 minutes timeout for vector DB initialization

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ai-interns:latest']

images:
  - 'gcr.io/$PROJECT_ID/ai-interns:latest'

timeout: 2400s  # 40 minutes total

options:
  machineType: 'E2_HIGHCPU_8'  # More CPU for faster builds
  diskSizeGb: 100
EOF

# 4. Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml .

# 5. Watch the build progress
# You'll see all the vector DB initialization happening in the cloud
```

## After Successful Build

Once Cloud Build completes:

```bash
# Check the image was created
gcloud container images list --filter="ai-interns"

# Deploy to Cloud Run
gcloud run deploy ai-interns \
  --image gcr.io/$(gcloud config get-value project)/ai-interns:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-api03-xxxxx \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10

# Get the service URL
gcloud run services describe ai-interns --region us-central1 --format='value(status.url)'
```

## Why Cloud Build is Better for Cloud Shell

| Factor | Local Docker Build | Cloud Build |
|--------|-------------------|-------------|
| Disk Space | Limited (~5-10GB in home dir) | 100GB+ per build |
| Build Speed | Slow (shared VM) | Fast (dedicated resources) |
| Memory | Limited | Configurable (up to 32GB) |
| CPU | 1-2 cores | Configurable (up to 32 cores) |
| Cost | Free (Cloud Shell) | $0.003/build-minute (first 120 min/day free) |
| Reliability | Can timeout/crash | Robust, automatic retries |

## Cost Estimate for Cloud Build

Your build will take ~20 minutes:
- First 120 minutes per day: **FREE**
- After that: $0.003/minute = ~$0.06 per build
- **Likely cost: $0** (within free tier)

## Summary

**For Cloud Shell users:**
1. ❌ Don't build locally in Cloud Shell (disk space issues)
2. ✅ Use Cloud Build instead (designed for this)
3. ✅ Deploy directly to Cloud Run
4. ✅ Get a public URL instantly

**Quick command:**
```bash
# One command to build and get your app running
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/ai-interns . && \
gcloud run deploy ai-interns \
  --image gcr.io/$(gcloud config get-value project)/ai-interns \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your-key-here \
  --memory 2Gi
```
