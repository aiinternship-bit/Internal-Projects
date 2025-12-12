"""
Google Cloud Storage Utilities for Milvus Database (eDelivery)
Downloads and uploads Milvus database from/to GCS bucket
Follows the same pattern as Zebra ChromaDB GCS utilities
"""
from google.cloud import storage
import os
from pathlib import Path
from typing import Optional


def download_milvus_from_gcs(
    bucket_name: str,
    gcs_file_path: str,
    local_db_path: str,
    credentials_path: Optional[str] = None
) -> bool:
    """
    Download Milvus database file from Google Cloud Storage to local filesystem.

    Args:
        bucket_name: Name of the GCS bucket (e.g., 'edeliverydata')
        gcs_file_path: File path in GCS (e.g., 'milvus_edelivery.db')
        local_db_path: Local path where Milvus DB should be stored (e.g., './milvus_edelivery.db')
        credentials_path: Optional path to service account JSON key file
                         If not provided, uses default credentials

    Returns:
        bool: True if successful, False otherwise

    Example:
        >>> success = download_milvus_from_gcs(
        ...     bucket_name='edeliverydata',
        ...     gcs_file_path='milvus_edelivery.db',
        ...     local_db_path='./milvus_edelivery.db'
        ... )
    """
    try:
        # Set credentials if provided
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

        # Initialize GCS client
        print(f"Connecting to GCS bucket: {bucket_name}")
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        # Get the blob
        blob = bucket.blob(gcs_file_path)

        # Ensure local directory exists
        local_path = Path(local_db_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        print(f"  Downloading: gs://{bucket_name}/{gcs_file_path} -> {local_db_path}")
        blob.download_to_filename(str(local_path))

        # Check file size
        file_size = local_path.stat().st_size
        print(f"✓ Successfully downloaded Milvus database ({file_size:,} bytes)")
        print(f"  Source: gs://{bucket_name}/{gcs_file_path}")
        print(f"  Destination: {local_db_path}")
        return True

    except Exception as e:
        print(f"✗ Error downloading Milvus database from GCS: {e}")
        import traceback
        traceback.print_exc()
        return False


def upload_milvus_to_gcs(
    local_db_path: str,
    bucket_name: str,
    gcs_file_path: str,
    credentials_path: Optional[str] = None
) -> bool:
    """
    Upload Milvus database file from local filesystem to Google Cloud Storage.

    Args:
        local_db_path: Local path where Milvus DB is stored (e.g., './milvus_edelivery.db')
        bucket_name: Name of the GCS bucket (e.g., 'edeliverydata')
        gcs_file_path: File path in GCS to store the DB (e.g., 'milvus_edelivery.db')
        credentials_path: Optional path to service account JSON key file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Set credentials if provided
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

        # Check if local file exists
        local_path = Path(local_db_path)
        if not local_path.exists():
            print(f"✗ Local Milvus database not found at {local_db_path}")
            return False

        # Initialize GCS client
        print(f"Connecting to GCS bucket: {bucket_name}")
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        # Upload file
        blob = bucket.blob(gcs_file_path)
        file_size = local_path.stat().st_size
        print(f"  Uploading: {local_db_path} ({file_size:,} bytes) -> gs://{bucket_name}/{gcs_file_path}")
        blob.upload_from_filename(str(local_path))

        print(f"✓ Successfully uploaded Milvus database")
        print(f"  Source: {local_db_path}")
        print(f"  Destination: gs://{bucket_name}/{gcs_file_path}")
        return True

    except Exception as e:
        print(f"✗ Error uploading Milvus database to GCS: {e}")
        import traceback
        traceback.print_exc()
        return False


def milvus_exists_locally(local_db_path: str) -> bool:
    """
    Check if Milvus database exists locally.

    Args:
        local_db_path: Local path to check for Milvus database

    Returns:
        bool: True if Milvus database file exists locally
    """
    db_path = Path(local_db_path)

    if db_path.exists() and db_path.is_file():
        file_size = db_path.stat().st_size
        print(f"✓ Milvus database found locally at {local_db_path} ({file_size:,} bytes)")
        return True
    else:
        print(f"✗ Milvus database not found locally at {local_db_path}")
        return False


def milvus_exists_in_gcs(bucket_name: str, gcs_file_path: str) -> bool:
    """
    Check if Milvus database exists in GCS bucket.

    Args:
        bucket_name: GCS bucket name
        gcs_file_path: File path in GCS

    Returns:
        bool: True if database exists in GCS
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_file_path)

        if blob.exists():
            # Get file size
            blob.reload()
            file_size = blob.size
            print(f"✓ Milvus database found in GCS: gs://{bucket_name}/{gcs_file_path}")
            print(f"  Size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
            return True
        else:
            print(f"✗ Milvus database not found in GCS: gs://{bucket_name}/{gcs_file_path}")
            return False
    except Exception as e:
        print(f"✗ Error checking GCS: {e}")
        return False


def ensure_milvus_available(
    local_db_path: str,
    bucket_name: str = "edeliverydata",
    gcs_file_path: str = "milvus_edelivery.db",
    force_download: bool = False
) -> bool:
    """
    Ensure Milvus database is available locally, downloading from GCS if necessary.
    This is the main function to call at runtime startup (e.g., in Cloud Run).

    Checks if database exists in GCS bucket before attempting download.

    Args:
        local_db_path: Local path where Milvus DB should be stored
        bucket_name: GCS bucket name containing Milvus DB
        gcs_file_path: File path in GCS
        force_download: If True, download even if local copy exists

    Returns:
        bool: True if Milvus database is available, False otherwise
    """
    # Check if already exists locally
    if not force_download and milvus_exists_locally(local_db_path):
        print("Using existing local Milvus database")
        return True

    # Check if database exists in GCS before attempting download
    print(f"Checking if Milvus database exists in GCS...")
    if not milvus_exists_in_gcs(bucket_name, gcs_file_path):
        print(f"")
        print(f"❌ Cannot proceed: Database does not exist in gs://{bucket_name}/{gcs_file_path}")
        print(f"")
        print(f"   Please ensure the database is uploaded to GCS:")
        print(f"   1. Build the database locally, OR")
        print(f"   2. Upload existing database using:")
        print(f"      python3 -m src.milvus_gcs_utils upload --bucket {bucket_name} --gcs-path {gcs_file_path}")
        print(f"")
        return False

    # Download from GCS
    print(f"Downloading Milvus database from GCS...")
    return download_milvus_from_gcs(
        bucket_name=bucket_name,
        gcs_file_path=gcs_file_path,
        local_db_path=local_db_path
    )


if __name__ == "__main__":
    # Test the download and upload
    import argparse

    parser = argparse.ArgumentParser(description="Manage Milvus database in GCS")
    parser.add_argument(
        "action",
        choices=["download", "upload"],
        help="Action to perform"
    )
    parser.add_argument(
        "--bucket",
        default="edeliverydata",
        help="GCS bucket name (default: edeliverydata)"
    )
    parser.add_argument(
        "--gcs-path",
        default="milvus_edelivery.db",
        help="File path in GCS (default: milvus_edelivery.db)"
    )
    parser.add_argument(
        "--local-path",
        default="./milvus_edelivery.db",
        help="Local path to Milvus database (default: ./milvus_edelivery.db)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download even if local copy exists"
    )

    args = parser.parse_args()

    if args.action == "download":
        success = ensure_milvus_available(
            local_db_path=args.local_path,
            bucket_name=args.bucket,
            gcs_file_path=args.gcs_path,
            force_download=args.force
        )
        if success:
            print("\n✅ Milvus database is ready!")
            exit(0)
        else:
            print("\n❌ Failed to ensure Milvus database availability")
            exit(1)
    elif args.action == "upload":
        success = upload_milvus_to_gcs(
            local_db_path=args.local_path,
            bucket_name=args.bucket,
            gcs_file_path=args.gcs_path
        )
        if success:
            print("\n✅ Milvus database uploaded successfully!")
            exit(0)
        else:
            print("\n❌ Failed to upload Milvus database")
            exit(1)
