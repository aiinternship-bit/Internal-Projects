#!/bin/bash
# Complete Deployment Script for eDelivery RAG System
# This script handles both database building and Cloud Run deployment

set -e  # Exit on error

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="edelivery-rag-api"
BUCKET_NAME="edeliverydata"
EXCEL_FILE_PATH="edeliverydata/eDelivery_AIeDelivery_Database_V1.xlsx"
DB_FILE_PATH="milvus_edelivery.db"

# Colors for output
GREEN='\033[0.32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}eDelivery RAG System Deployment${NC}"
echo -e "${BLUE}============================================${NC}"

# Step 1: Build Milvus Database
echo -e "\n${YELLOW}[Step 1/3] Building Milvus Vector Database...${NC}"
echo "This will:"
echo "  - Read Excel from gs://${BUCKET_NAME}/${EXCEL_FILE_PATH}"
echo "  - Build vector database with embeddings"
echo "  - Upload to gs://${BUCKET_NAME}/${DB_FILE_PATH}"
echo ""
read -p "Do you want to build/rebuild the database? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Submitting Cloud Build job..."
    gcloud builds submit \
        --config=cloudbuild-build-db.yaml \
        --project=${PROJECT_ID} \
        --substitutions=_BUCKET_NAME=${BUCKET_NAME},_EXCEL_PATH=${EXCEL_FILE_PATH},_DB_PATH=${DB_FILE_PATH}

    echo -e "${GREEN}✓ Database build completed${NC}"
else
    echo "Skipping database build..."
fi

# Step 2: Build and Push Docker Image
echo -e "\n${YELLOW}[Step 2/3] Building and Pushing Docker Image...${NC}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

gcloud builds submit \
    --tag ${IMAGE_NAME} \
    --project=${PROJECT_ID}

echo -e "${GREEN}✓ Docker image built and pushed${NC}"

# Step 3: Deploy to Cloud Run
echo -e "\n${YELLOW}[Step 3/3] Deploying to Cloud Run...${NC}"

gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --allow-unauthenticated \
    --set-env-vars "DB_PATH=/app/milvus_edelivery.db,GCS_BUCKET=${BUCKET_NAME},GCS_DB_PATH=${DB_FILE_PATH}" \
    --service-account "${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --format 'value(status.url)')

echo -e "\n${BLUE}============================================${NC}"
echo -e "${GREEN}✅ Deployment Completed Successfully!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Test the API:"
echo "  Health Check:"
echo "    curl ${SERVICE_URL}/health"
echo ""
echo "  Query Example:"
echo "    curl -X POST ${SERVICE_URL}/query \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"question\": \"What is the digital delivery system?\"}'"
echo ""
echo -e "${BLUE}============================================${NC}"
