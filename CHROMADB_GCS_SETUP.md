# ChromaDB GCS Storage Setup

This document explains how the Zebra Project ChromaDB is stored in Google Cloud Storage and loaded at runtime.

## Overview

Previously, the ChromaDB was stored locally in `./Zebra Project/chroma_db/`, which caused issues during GCP deployment because:
- The directory was lost when the Docker build completed
- The vector database wasn't available at runtime

**Solution**: Store ChromaDB in a Google Cloud Storage bucket and download it when the application starts.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Google Cloud Storage                       │
│  Bucket: zebra-chromadb-storage             │
│  ├── chroma_db/                             │
│      ├── chroma.sqlite3                     │
│      └── f8338f5d-.../                      │
│          ├── header.bin                     │
│          ├── link_lists.bin                 │
│          ├── data_level0.bin                │
│          └── length.bin                     │
└─────────────────────────────────────────────┘
                    │
                    │ Download at runtime
                    ▼
┌─────────────────────────────────────────────┐
│  Cloud Run Container                        │
│  /app/Zebra Project/chroma_db/              │
│  (Downloaded from GCS on first use)         │
└─────────────────────────────────────────────┘
```

## Files Modified

### 1. **New File**: `Zebra Project/src/chromadb_gcs_utils.py`
Utility functions to:
- Download ChromaDB from GCS to local filesystem
- Check if ChromaDB exists locally
- Ensure ChromaDB is available (download if needed)

### 2. **Modified**: `AI-Interns/app.py`
Updated `get_zebra_rag()` function to:
- Check if ChromaDB exists locally
- Download from GCS if not available
- Initialize Zebra RAG with the downloaded database

### 3. **Modified**: `.gitignore`
Uncommented lines to exclude `chroma_db/` directories from version control since they're now stored in GCS.

## Configuration

The system uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `ZEBRA_CHROMADB_BUCKET` | `zebra-chromadb-storage` | GCS bucket name |
| `ZEBRA_CHROMADB_FOLDER` | `chroma_db` | Folder path in GCS bucket |

## How It Works

1. **First Request to Zebra Project**:
   - User queries the Zebra printer search
   - `get_zebra_rag()` is called (lazy initialization)
   - System checks if ChromaDB exists locally
   - If not, downloads from GCS bucket `zebra-chromadb-storage/chroma_db/`
   - Initializes ChromaDB and PrinterRAG
   - Returns results

2. **Subsequent Requests**:
   - ChromaDB is already available locally
   - No download occurs
   - Queries run immediately

## Deployment Steps

### 1. Upload ChromaDB to GCS (One-time setup - Already Done!)
✅ You've already uploaded to: `zebra-chromadb-storage/chroma_db/`

### 2. Set Permissions for Cloud Run Service Account

Ensure your Cloud Run service account has permission to read from the GCS bucket:

```bash
# Get your Cloud Run service account
# Usually: PROJECT_NUMBER-compute@developer.gserviceaccount.com

# Grant Storage Object Viewer role
gcloud projects add-iam-policy-binding acl-ai-projects \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

Or via Google Cloud Console:
1. Go to **Cloud Storage** → **Browser**
2. Click on `zebra-chromadb-storage` bucket
3. Go to **Permissions** tab
4. Click **Grant Access**
5. Add your Cloud Run service account
6. Assign role: **Storage Object Viewer**

### 3. Deploy to Cloud Run

Build and deploy as usual:

```bash
# Build the Docker image
gcloud builds submit --tag gcr.io/acl-ai-projects/ai-interns

# Deploy to Cloud Run
gcloud run deploy ai-interns \
    --image gcr.io/acl-ai-projects/ai-interns \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 300
```

The ChromaDB will be automatically downloaded on first use.

## Local Development

For local development, you have two options:

### Option 1: Use Local ChromaDB
Keep your local `./Zebra Project/chroma_db/` directory. The system will detect it and use it without downloading from GCS.

### Option 2: Test GCS Download
Delete your local `chroma_db` directory and run the app. It will download from GCS just like in production.

## Updating ChromaDB

When you need to update the ChromaDB (add new printers, re-index, etc.):

1. **Generate new ChromaDB locally**:
   ```bash
   cd "Zebra Project"
   python src/vector_db_ingest.py ./output --clear
   ```

2. **Upload to GCS**:
   - Delete the old `chroma_db` folder from the GCS bucket
   - Upload the new `chroma_db` folder via Google Cloud Console
   - Or use `gsutil`:
     ```bash
     gsutil -m rm -r gs://zebra-chromadb-storage/chroma_db/
     gsutil -m cp -r "Zebra Project/chroma_db" gs://zebra-chromadb-storage/
     ```

3. **Restart Cloud Run**:
   - Either redeploy or just restart the existing deployment
   - The new ChromaDB will be downloaded on first use

## Manual Testing Script

You can test the download functionality manually:

```bash
cd "Zebra Project/src"
python chromadb_gcs_utils.py \
    --bucket zebra-chromadb-storage \
    --gcs-folder chroma_db \
    --local-path ./test_download \
    --force
```

This will download ChromaDB to `./test_download/` for verification.

## Troubleshooting

### Issue: "ChromaDB could not be loaded from GCS or local storage"

**Causes**:
- GCS bucket doesn't exist
- Incorrect bucket name or folder path
- Service account lacks permissions
- Network connectivity issues

**Solutions**:
1. Verify bucket exists: https://console.cloud.google.com/storage/browser
2. Check bucket name in environment variables
3. Verify service account permissions
4. Check Cloud Run logs for detailed error messages

### Issue: Slow first request

**Expected**: The first request to Zebra Project will be slower because it downloads ChromaDB from GCS (typically 2-5 seconds depending on database size).

**Solution**: This is normal. Subsequent requests will be fast.

### Issue: Database seems outdated

**Solution**:
1. Check when the GCS ChromaDB was last updated
2. Re-upload the latest ChromaDB to GCS
3. Restart or redeploy Cloud Run service

## Cost Considerations

- **Storage Cost**: Google Cloud Storage charges ~$0.020 per GB/month
- **Network Egress**: Download from GCS to Cloud Run (same region) is typically free
- **Operations**: GET operations are very cheap (~$0.0004 per 1000 requests)

For a typical ChromaDB (~50-100MB), costs are negligible (<$0.01/month).

## Security

- ChromaDB contains public Zebra printer specifications (no sensitive data)
- Bucket is private by default
- Access controlled via IAM (Cloud Run service account only)
- No public access required

## Summary

✅ ChromaDB stored in GCS: `gs://zebra-chromadb-storage/chroma_db/`
✅ Automatically downloaded on first use
✅ Cached locally for subsequent requests
✅ No manual intervention required during deployment
✅ Easy to update (just upload new version to GCS)

The system is now production-ready and will work seamlessly on Google Cloud Run!
