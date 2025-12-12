#!/usr/bin/env python3
"""
Build Milvus Vector Database from GCS Excel File
Reads Excel from GCS bucket, builds Milvus database, and uploads it back to GCS
"""
import argparse
import os
from pathlib import Path
from src.structure_db import StructureVectorDB
from src.content_db import ContentVectorDB
from src.gcs_utils import read_xlsx_from_gcs
from src.milvus_gcs_utils import upload_milvus_to_gcs
from src import config


def build_and_upload_milvus_db(
    bucket_name: str = "edeliverydata",
    excel_file_path: str = "edeliverydata/eDelivery_AIeDelivery_Database_V1.xlsx",
    local_db_path: str = config.DB_PATH,
    gcs_db_path: str = "milvus_edelivery.db",
    drop_existing: bool = True
):
    """
    Complete pipeline to build Milvus database from GCS Excel and upload back to GCS.

    Args:
        bucket_name: GCS bucket name containing the Excel file
        excel_file_path: Path to Excel file in the bucket
        local_db_path: Local path to build Milvus database
        gcs_db_path: Path in GCS bucket to store the Milvus database
        drop_existing: Whether to drop existing collections
    """
    print("\n" + "="*80)
    print("BUILDING MILVUS DATABASE FROM GCS EXCEL FILE")
    print("="*80)
    print(f"Excel Source: gs://{bucket_name}/{excel_file_path}")
    print(f"Local DB Path: {local_db_path}")
    print(f"GCS DB Upload: gs://{bucket_name}/{gcs_db_path}")
    print("="*80)

    # Step 1: Download and read Excel file from GCS
    print("\n[Step 1/5] Reading Excel file from GCS...")
    from google.cloud import storage
    import pandas as pd
    import io
    import tempfile

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(excel_file_path)
        file_content = blob.download_as_bytes()

        # Save to temporary file for processing
        temp_excel_path = Path(tempfile.gettempdir()) / "temp_edelivery.xlsx"
        with open(temp_excel_path, 'wb') as f:
            f.write(file_content)

        print(f"✓ Excel file downloaded ({len(file_content):,} bytes)")
        print(f"  Temporary location: {temp_excel_path}")

    except Exception as e:
        print(f"✗ Error downloading Excel file from GCS: {e}")
        return False

    # Step 2: Build structure database
    print("\n[Step 2/5] Building Structure Database...")
    try:
        structure_db = StructureVectorDB(local_db_path)
        structure_db.build_from_excel(str(temp_excel_path), drop_existing=drop_existing)
        print("✓ Structure database built successfully")
    except Exception as e:
        print(f"✗ Error building structure database: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Build content database
    print("\n[Step 3/5] Building Content Database...")
    print("⚠️  This may take several minutes to hours depending on file size!")
    try:
        content_db = ContentVectorDB(local_db_path)
        content_db.build_from_excel(str(temp_excel_path), drop_existing=drop_existing)
        print("✓ Content database built successfully")
    except Exception as e:
        print(f"✗ Error building content database: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Clean up temporary file
    print("\n[Step 4/5] Cleaning up temporary files...")
    try:
        temp_excel_path.unlink()
        print(f"✓ Removed temporary file: {temp_excel_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not remove temporary file: {e}")

    # Step 5: Upload Milvus database to GCS
    print("\n[Step 5/5] Uploading Milvus database to GCS...")
    try:
        success = upload_milvus_to_gcs(
            local_db_path=local_db_path,
            bucket_name=bucket_name,
            gcs_file_path=gcs_db_path
        )

        if success:
            print("\n" + "="*80)
            print("✅ DATABASE BUILD AND UPLOAD COMPLETE!")
            print("="*80)
            print(f"Milvus database is now available at:")
            print(f"  gs://{bucket_name}/{gcs_db_path}")
            print("\nTo use this database in Cloud Run:")
            print(f"  1. Call ensure_milvus_available() at runtime startup")
            print(f"  2. It will download from gs://{bucket_name}/{gcs_db_path}")
            print(f"  3. Use the local database for queries")
            print("="*80)
            return True
        else:
            print("\n✗ Failed to upload Milvus database to GCS")
            return False

    except Exception as e:
        print(f"\n✗ Error uploading Milvus database to GCS: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="Build Milvus database from GCS Excel file and upload to GCS"
    )
    parser.add_argument(
        "--bucket",
        default="edeliverydata",
        help="GCS bucket name (default: edeliverydata)"
    )
    parser.add_argument(
        "--excel-path",
        default="edeliverydata/eDelivery_AIeDelivery_Database_V1.xlsx",
        help="Path to Excel file in bucket (default: edeliverydata/eDelivery_AIeDelivery_Database_V1.xlsx)"
    )
    parser.add_argument(
        "--local-db",
        default=config.DB_PATH,
        help=f"Local path to build Milvus database (default: {config.DB_PATH})"
    )
    parser.add_argument(
        "--gcs-db-path",
        default="milvus_edelivery.db",
        help="Path in GCS bucket to store Milvus database (default: milvus_edelivery.db)"
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Keep existing collections (do not drop)"
    )

    args = parser.parse_args()

    success = build_and_upload_milvus_db(
        bucket_name=args.bucket,
        excel_file_path=args.excel_path,
        local_db_path=args.local_db,
        gcs_db_path=args.gcs_db_path,
        drop_existing=not args.keep_existing
    )

    if success:
        print("\n✅ Build completed successfully!")
        exit(0)
    else:
        print("\n❌ Build failed!")
        exit(1)


if __name__ == "__main__":
    main()
