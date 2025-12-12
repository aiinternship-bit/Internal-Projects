#!/bin/bash
# Build Milvus Database Only
# Use this script to build/rebuild just the vector database

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
BUCKET_NAME="edeliverydata"
EXCEL_FILE_PATH="edeliverydata/eDelivery_AIeDelivery_Database_V1.xlsx"
DB_FILE_PATH="milvus_edelivery.db"

echo "============================================"
echo "Building Milvus Vector Database"
echo "============================================"
echo "Project: ${PROJECT_ID}"
echo "Source: gs://${BUCKET_NAME}/${EXCEL_FILE_PATH}"
echo "Output: gs://${BUCKET_NAME}/${DB_FILE_PATH}"
echo "============================================"
echo ""

# Submit Cloud Build job
echo "Submitting Cloud Build job..."
gcloud builds submit \
    --config=cloudbuild-build-db.yaml \
    --project=${PROJECT_ID}

echo ""
echo "============================================"
echo "✅ Database build completed!"
echo "============================================"
echo "Database location: gs://${BUCKET_NAME}/${DB_FILE_PATH}"
echo ""
echo "You can now deploy the Cloud Run service with:"
echo "  ./deploy.sh"
echo "============================================"
