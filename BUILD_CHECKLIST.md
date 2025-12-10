# Docker Build Checklist

## Pre-Build Requirements

### ✅ System Requirements
- [ ] Docker Desktop installed and running
- [ ] At least 10GB free disk space (recommended: 15-20GB for build cache)
  - Base image: ~200MB
  - Python dependencies: ~2GB
  - Vector databases + ML models: ~1-1.5GB
  - Build cache: ~500MB
  - **Total image size: ~3.5GB**
- [ ] Stable internet connection (for downloading dependencies)

### ✅ Configuration Files

- [ ] `.env` file exists in `Internal-Projects/` directory
  ```bash
  cp .env.example .env
  ```
- [ ] `ANTHROPIC_API_KEY` set in `.env`
  ```bash
  ANTHROPIC_API_KEY=sk-ant-api03-...
  ```

### ✅ Optional: GCS Configuration (if using Cloud Storage)

- [ ] `USE_GCS=true` in `.env`
- [ ] `GCS_BUCKET_NAME` set in `.env`
- [ ] Service account key file downloaded
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` path set in `.env`

## Build Process

### Option 1: Quick Test Build

```bash
cd Internal-Projects
./build-test.sh
```

This script will:
- ✓ Check if Docker is running
- ✓ Verify .env file exists
- ✓ Build the image
- ✓ Save build log to `build.log`

### Option 2: Manual Build

```bash
cd Internal-Projects
docker build -t ai-interns .
```

### Option 3: Docker Compose Build

```bash
cd Internal-Projects
docker-compose build
```

## Expected Build Time

- **First build**: 15-25 minutes (downloading base images, dependencies, and initializing vector databases)
  - Base image download: 1-2 minutes
  - Python dependencies: 5-10 minutes
  - **Vector database initialization: 5-10 minutes**
    - Zebra Project ChromaDB: ~2-3 minutes (32 JSON files)
    - GEN AI Agent Milvus: ~3-7 minutes (Excel file processing and embeddings)
- **Subsequent builds**: 2-5 minutes (using cached layers, vector DBs already initialized)

## Build Output Verification

### What Happens During Build

During the Docker build, the following happens automatically:

1. **System dependencies installed** (gcc, g++, git, curl, etc.)
2. **Python packages installed** from requirements.txt
3. **Vector databases initialized**:
   - **Zebra Project ChromaDB**: Processes 32 JSON printer specification files
   - **GEN AI Agent Milvus**: Processes Excel file and generates embeddings

You'll see output like this during vector DB initialization:

```
Step X/Y : RUN python init_vector_dbs.py || echo "Warning: Vector DB initialization had issues, continuing..."
 ---> Running in abc123def456
================================================================================
VECTOR DATABASE INITIALIZATION
================================================================================

================================================================================
Initializing Zebra Project ChromaDB...
================================================================================
Found 32 JSON files to process
...
✅ Zebra ChromaDB initialized successfully!

================================================================================
Initializing GEN AI Agent Milvus...
================================================================================
Building content database from: /app/GEN AI Agent/Archive/eDelivery_AIeDelivery_Database_V1.xlsx
...
✅ GEN AI Milvus initialized successfully!
```

### Successful Build Indicators

```bash
# Check if image was created
docker images | grep ai-interns

# Should output something like:
# ai-interns    latest    abc123def456    20 minutes ago    3.5GB
```

Note: Image size will be larger (~3.5GB) due to vector databases and ML models.

### Test the Built Image

```bash
# Test basic imports
docker run --rm ai-interns python -c "import flask; import anthropic; print('✓ All imports successful')"

# Test vector databases exist
docker run --rm ai-interns python -c "import os; print('Zebra ChromaDB:', os.path.exists('/app/Zebra Project/chroma_db')); print('GEN AI Milvus:', os.path.exists('/app/GEN AI Agent/Archive/milvus_edelivery.db'))"
```

## Common Build Issues & Fixes

### Issue 1: "No space left on device"

**Solution:**
```bash
# Clean up Docker
docker system prune -a --volumes

# Free up space
docker image prune -a
```

### Issue 2: "requirements.txt not found"

**Solution:**
```bash
# Make sure you're in the Internal-Projects directory
pwd  # Should end with /Internal-Projects
ls requirements.txt  # Should exist
```

### Issue 3: Dependency installation failures

**Solution:**
```bash
# Try building with --no-cache
docker build --no-cache -t ai-interns .
```

### Issue 4: "Cannot connect to the Docker daemon"

**Solution:**
- Start Docker Desktop
- Wait for it to fully initialize
- Run `docker info` to verify connection

### Issue 5: Torch/PyTorch installation timeout

**Solution:**
```bash
# Use a larger timeout
docker build --network=host -t ai-interns .
```

### Issue 6: Vector database initialization warnings

**Problem:** You see warnings during vector DB initialization but build continues

**Solution:**
This is expected behavior. The build will continue even if vector DB initialization has issues. The warning means:
- Data files may be missing (JSON files or Excel file)
- Vector DBs will be empty but the container will still work
- You can initialize them later manually or with GCS

To verify what initialized successfully, check the build logs for:
```
✅ Zebra ChromaDB initialized successfully!
✅ GEN AI Milvus initialized successfully!
```

### Issue 7: "failed to read dockerfile" error

**Problem:**
```
ERROR: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

**Solution:**
You're in the wrong directory. Navigate to the Internal-Projects directory:
```bash
# Find your project
pwd

# Navigate to Internal-Projects
cd /path/to/Internal-Projects

# Verify Dockerfile exists
ls Dockerfile

# Then build
docker build -t ai-interns .
```

## Post-Build: Running the Container

### Using Docker Compose (Recommended)

```bash
docker-compose up -d

# View logs
docker-compose logs -f

# Access application
open http://localhost:5001
```

### Using Docker CLI

```bash
docker run -d \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd)/AI-Interns/conversations.db:/app/AI-Interns/conversations.db \
  --name ai-interns-app \
  ai-interns

# View logs
docker logs -f ai-interns-app

# Access application
open http://localhost:5001
```

## Build Optimization Tips

### 1. Use Build Cache Efficiently

```bash
# If only code changes (not dependencies)
docker-compose build --parallel
```

### 2. Multi-Stage Build (Future Enhancement)

Consider splitting into:
- Base image with system dependencies
- Dependencies layer
- Application code layer

### 3. Layer Caching

The Dockerfile is already optimized:
1. System dependencies (rarely change)
2. Requirements file (occasionally changes)
3. Application code (frequently changes)

## Deployment Checklist

### Local Development
- [x] Build successful
- [ ] Container runs without errors
- [ ] Can access http://localhost:5001
- [ ] API key works (test chat functionality)
- [ ] Database persistence works

### Production (Cloud Run)
- [ ] Environment variables configured
- [ ] GCS credentials set up (if using)
- [ ] Health check endpoint working
- [ ] Container tagged and pushed to registry

## Troubleshooting Commands

```bash
# Check Docker status
docker info

# List images
docker images

# List running containers
docker ps

# View container logs
docker logs <container-name>

# Inspect image
docker inspect ai-interns

# Shell into running container
docker exec -it ai-interns-app /bin/bash

# Remove failed builds
docker rmi $(docker images -f "dangling=true" -q)
```

## Build Logs

Build logs are saved to `build.log` when using `./build-test.sh`

To review:
```bash
# View full log
cat build.log

# Search for errors
grep -i error build.log

# View last 50 lines
tail -50 build.log
```

## Success Criteria

Your build is successful when:

1. ✅ Docker build completes without errors
2. ✅ Image appears in `docker images` list
3. ✅ Test import command succeeds
4. ✅ Container starts and stays running
5. ✅ Application accessible at http://localhost:5001
6. ✅ Health check passes

## Next Steps After Successful Build

1. Test all features:
   - Homepage loads
   - Can create new conversation
   - Chat functionality works
   - Conversation persistence works
   - Can switch conversations
   - Can delete conversations

2. Deploy to production:
   - Tag image: `docker tag ai-interns gcr.io/your-project/ai-interns:latest`
   - Push to registry: `docker push gcr.io/your-project/ai-interns:latest`
   - Deploy to Cloud Run

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
