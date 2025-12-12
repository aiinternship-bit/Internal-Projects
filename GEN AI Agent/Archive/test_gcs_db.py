#!/usr/bin/env python3
"""
Test script to verify Milvus database exists in GCS and can be downloaded
"""
from src.milvus_gcs_utils import milvus_exists_in_gcs, ensure_milvus_available
import sys

def main():
    bucket_name = "edeliverydata"
    gcs_db_path = "milvus_edelivery.db"
    local_db_path = "./milvus_edelivery.db"

    print("="*80)
    print("Testing Milvus Database GCS Access")
    print("="*80)
    print(f"Bucket: {bucket_name}")
    print(f"GCS Path: {gcs_db_path}")
    print(f"Local Path: {local_db_path}")
    print("="*80)
    print()

    # Step 1: Check if database exists in GCS
    print("Step 1: Checking if database exists in GCS bucket...")
    print("-"*80)
    exists_in_gcs = milvus_exists_in_gcs(bucket_name, gcs_db_path)
    print()

    if not exists_in_gcs:
        print("❌ Database not found in GCS!")
        print()
        print("Please upload the database to GCS:")
        print(f"  gsutil cp milvus_edelivery.db gs://{bucket_name}/{gcs_db_path}")
        print()
        sys.exit(1)

    # Step 2: Test download
    print("Step 2: Testing download from GCS...")
    print("-"*80)
    success = ensure_milvus_available(
        local_db_path=local_db_path,
        bucket_name=bucket_name,
        gcs_file_path=gcs_db_path,
        force_download=False
    )
    print()

    if success:
        print("="*80)
        print("✅ SUCCESS! Database is ready to use")
        print("="*80)
        print()
        print("You can now:")
        print("  1. Run queries locally using query_from_gcs.py")
        print("  2. Deploy to Cloud Run using deploy.sh")
        print()
        sys.exit(0)
    else:
        print("="*80)
        print("❌ FAILED to ensure database availability")
        print("="*80)
        sys.exit(1)


if __name__ == "__main__":
    main()
