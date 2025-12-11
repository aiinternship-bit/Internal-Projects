"""
Google Cloud Storage Utilities for ChromaDB
Downloads ChromaDB from GCS bucket to local storage
"""
from google.cloud import storage
import os
from pathlib import Path
from typing import Optional


def download_chromadb_from_gcs(
    bucket_name: str,
    gcs_folder: str,
    local_db_path: str,
    credentials_path: Optional[str] = None
) -> bool:
    """
    Download ChromaDB directory from Google Cloud Storage to local filesystem.

    Args:
        bucket_name: Name of the GCS bucket (e.g., 'zebra-chromadb-storage')
        gcs_folder: Folder path in GCS containing chroma_db (e.g., 'chroma_db')
        local_db_path: Local path where ChromaDB should be stored (e.g., './chroma_db')
        credentials_path: Optional path to service account JSON key file
                         If not provided, uses default credentials

    Returns:
        bool: True if successful, False otherwise

    Example:
        >>> success = download_chromadb_from_gcs(
        ...     bucket_name='zebra-chromadb-storage',
        ...     gcs_folder='chroma_db',
        ...     local_db_path='/app/Zebra Project/chroma_db'
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

        # Ensure local directory exists
        local_path = Path(local_db_path)
        local_path.mkdir(parents=True, exist_ok=True)

        # List all blobs in the GCS folder
        blobs = bucket.list_blobs(prefix=gcs_folder)

        downloaded_count = 0
        for blob in blobs:
            # Skip if it's just a folder marker
            if blob.name.endswith('/'):
                continue

            # Calculate local file path
            # Remove the gcs_folder prefix to get relative path
            relative_path = blob.name[len(gcs_folder):].lstrip('/')
            local_file_path = local_path / relative_path

            # Create parent directories if needed
            local_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Download the file
            print(f"  Downloading: {blob.name} -> {local_file_path}")
            blob.download_to_filename(str(local_file_path))
            downloaded_count += 1

        if downloaded_count == 0:
            print(f"⚠️  Warning: No files found in gs://{bucket_name}/{gcs_folder}")
            return False

        print(f"✓ Successfully downloaded {downloaded_count} files from GCS")
        print(f"  Source: gs://{bucket_name}/{gcs_folder}")
        print(f"  Destination: {local_db_path}")
        return True

    except Exception as e:
        print(f"✗ Error downloading ChromaDB from GCS: {e}")
        import traceback
        traceback.print_exc()
        return False


def chromadb_exists_locally(local_db_path: str) -> bool:
    """
    Check if ChromaDB exists locally.

    Args:
        local_db_path: Local path to check for ChromaDB

    Returns:
        bool: True if ChromaDB files exist locally
    """
    db_path = Path(local_db_path)

    # Check for chroma.sqlite3 file
    sqlite_file = db_path / "chroma.sqlite3"

    if sqlite_file.exists():
        print(f"✓ ChromaDB found locally at {local_db_path}")
        return True
    else:
        print(f"✗ ChromaDB not found locally at {local_db_path}")
        return False


def ensure_chromadb_available(
    local_db_path: str,
    bucket_name: str = "zebra-chromadb-storage",
    gcs_folder: str = "chroma_db",
    force_download: bool = False
) -> bool:
    """
    Ensure ChromaDB is available locally, downloading from GCS if necessary.

    Args:
        local_db_path: Local path where ChromaDB should be stored
        bucket_name: GCS bucket name containing ChromaDB
        gcs_folder: Folder path in GCS
        force_download: If True, download even if local copy exists

    Returns:
        bool: True if ChromaDB is available, False otherwise
    """
    # Check if already exists locally
    if not force_download and chromadb_exists_locally(local_db_path):
        print("Using existing local ChromaDB")
        return True

    # Download from GCS
    print(f"Downloading ChromaDB from GCS...")
    return download_chromadb_from_gcs(
        bucket_name=bucket_name,
        gcs_folder=gcs_folder,
        local_db_path=local_db_path
    )


if __name__ == "__main__":
    # Test the download
    import argparse

    parser = argparse.ArgumentParser(description="Download ChromaDB from GCS")
    parser.add_argument(
        "--bucket",
        default="zebra-chromadb-storage",
        help="GCS bucket name"
    )
    parser.add_argument(
        "--gcs-folder",
        default="chroma_db",
        help="Folder path in GCS"
    )
    parser.add_argument(
        "--local-path",
        default="./chroma_db",
        help="Local path to store ChromaDB"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download even if local copy exists"
    )

    args = parser.parse_args()

    success = ensure_chromadb_available(
        local_db_path=args.local_path,
        bucket_name=args.bucket,
        gcs_folder=args.gcs_folder,
        force_download=args.force
    )

    if success:
        print("\n✅ ChromaDB is ready!")
        exit(0)
    else:
        print("\n❌ Failed to ensure ChromaDB availability")
        exit(1)
