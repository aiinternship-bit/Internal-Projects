# Google Cloud Storage Setup Guide

This guide explains how to configure the Archive project to read XLSX files from Google Cloud Storage buckets instead of the local filesystem.

## Prerequisites

1. **Google Cloud Project**: You need an active GCP project
2. **GCS Bucket**: Create a bucket and upload your XLSX files
3. **Service Account**: Create a service account with Storage Object Viewer permissions

## Setup Steps

### 1. Install Dependencies

The required package is already in requirements.txt:

```bash
pip install google-cloud-storage>=2.10.0
```

### 2. Create Service Account (One-time setup)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Click **Create Service Account**
4. Fill in the details:
   - Name: `archive-gcs-reader`
   - Description: `Service account for reading XLSX files from GCS`
5. Grant role: **Storage Object Viewer**
6. Click **Done**

### 3. Generate Service Account Key

1. Click on the created service account
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Download the key file (e.g., `archive-gcs-key.json`)
6. Store it securely (never commit to git!)

### 4. Configure Environment Variables

Add to your `.env` file in `Internal-Projects/`:

```bash
# Google Cloud Storage Configuration
USE_GCS=true
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/archive-gcs-key.json
```

### 5. Upload XLSX Files to GCS

Using gsutil:
```bash
gsutil cp your-file.xlsx gs://your-bucket-name/path/to/file.xlsx
```

Or using the GCS Console:
1. Go to [Cloud Storage Browser](https://console.cloud.google.com/storage)
2. Select your bucket
3. Click **Upload files**

## Usage

### Option 1: Using the GCS Utility Directly

```python
from src.gcs_utils import read_xlsx_from_gcs

# Read from GCS bucket
df = read_xlsx_from_gcs(
    bucket_name="my-bucket",
    file_path="data/spreadsheet.xlsx"
)
```

### Option 2: Auto-detect Local vs GCS

```python
from src.gcs_utils import read_xlsx_from_local_or_gcs
import os

# Automatically uses GCS if USE_GCS=true in .env
use_gcs = os.getenv('USE_GCS', 'false').lower() == 'true'
bucket = os.getenv('GCS_BUCKET_NAME') if use_gcs else None

df = read_xlsx_from_local_or_gcs(
    file_path="data/spreadsheet.xlsx",
    bucket_name=bucket
)
```

### Option 3: Explicit Credentials Path

```python
from src.gcs_utils import read_xlsx_from_gcs

df = read_xlsx_from_gcs(
    bucket_name="my-bucket",
    file_path="data/spreadsheet.xlsx",
    credentials_path="/path/to/service-account-key.json"
)
```

## Docker/Cloud Run Deployment

### Using Service Account in Docker

**Option A: Mount credentials file**
```bash
docker run -d \
  -e USE_GCS=true \
  -e GCS_BUCKET_NAME=my-bucket \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/key.json \
  -v /path/to/key.json:/app/credentials/key.json:ro \
  ai-interns
```

**Option B: Use Workload Identity (Recommended for GKE/Cloud Run)**
```bash
# No credentials file needed - uses service account attached to the workload
docker run -d \
  -e USE_GCS=true \
  -e GCS_BUCKET_NAME=my-bucket \
  ai-interns
```

### Update docker-compose.yml

```yaml
services:
  ai-interns:
    environment:
      - USE_GCS=${USE_GCS:-false}
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcs-key.json
    volumes:
      - ./credentials/gcs-key.json:/app/credentials/gcs-key.json:ro
```

## Security Best Practices

1. **Never commit service account keys** to version control
2. **Use .gitignore** to exclude credential files:
   ```
   *.json
   credentials/
   *-key.json
   ```

3. **Least Privilege**: Only grant Storage Object Viewer role
4. **Rotate Keys**: Periodically rotate service account keys
5. **Use Workload Identity**: In production (Cloud Run/GKE), use Workload Identity instead of key files

## Troubleshooting

### Error: "Could not automatically determine credentials"

**Solution**: Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set correctly:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Error: "403 Forbidden"

**Solution**: Check service account permissions:
- Go to GCS bucket → Permissions
- Ensure service account has `Storage Object Viewer` role

### Error: "Bucket not found"

**Solution**: Verify bucket name and access:
```bash
gsutil ls gs://your-bucket-name
```

## Development vs Production

### Development (Local)
- Use local XLSX files
- Set `USE_GCS=false` in `.env`

### Production (Cloud Run)
- Use GCS buckets
- Set `USE_GCS=true`
- Use Workload Identity (no key files needed)

## Example: Migration from Local to GCS

**Before (Local):**
```python
df = pd.read_excel("data/spreadsheet.xlsx")
```

**After (GCS-compatible):**
```python
from src.gcs_utils import read_xlsx_from_local_or_gcs
import os

use_gcs = os.getenv('USE_GCS', 'false').lower() == 'true'
bucket = os.getenv('GCS_BUCKET_NAME') if use_gcs else None

df = read_xlsx_from_local_or_gcs(
    file_path="data/spreadsheet.xlsx",
    bucket_name=bucket
)
```

This works in both development (local files) and production (GCS) without code changes!

## Additional Resources

- [GCS Python Client Documentation](https://cloud.google.com/python/docs/reference/storage/latest)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
