"""
Google Cloud Storage Utilities
Handles reading XLSX files from GCS buckets
"""
from google.cloud import storage
import pandas as pd
import io
import os
from typing import Optional


def read_xlsx_from_gcs(bucket_name: str, file_path: str, credentials_path: Optional[str] = None) -> pd.DataFrame:
    """
    Read an XLSX file from Google Cloud Storage bucket

    Args:
        bucket_name: Name of the GCS bucket
        file_path: Path to the XLSX file within the bucket
        credentials_path: Optional path to service account JSON key file
                         If not provided, uses default credentials

    Returns:
        pandas.DataFrame: The data from the XLSX file

    Raises:
        Exception: If file cannot be read or parsed

    Example:
        >>> df = read_xlsx_from_gcs("my-bucket", "data/spreadsheet.xlsx")
        >>> print(df.head())
    """
    try:
        # Set credentials if provided
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        # Download the blob content into a BytesIO object
        # This keeps the file in memory, which is fine for smaller files.
        # For very large files, consider streaming or processing in chunks.
        file_content = blob.download_as_bytes()

        # Use pandas to read the XLSX file from the in-memory bytes
        df = pd.read_excel(io.BytesIO(file_content))

        print(f"✓ Successfully read XLSX file from gs://{bucket_name}/{file_path}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")

        return df

    except Exception as e:
        print(f"✗ Error reading XLSX file from GCS: {e}")
        raise


def read_xlsx_from_local_or_gcs(file_path: str, bucket_name: Optional[str] = None,
                                 credentials_path: Optional[str] = None) -> pd.DataFrame:
    """
    Read an XLSX file from either local filesystem or GCS bucket

    Args:
        file_path: Path to the XLSX file (local or GCS path)
        bucket_name: Optional GCS bucket name. If provided, reads from GCS
        credentials_path: Optional path to service account JSON key file

    Returns:
        pandas.DataFrame: The data from the XLSX file

    Example:
        >>> # Read from local file
        >>> df = read_xlsx_from_local_or_gcs("data/local_file.xlsx")

        >>> # Read from GCS
        >>> df = read_xlsx_from_local_or_gcs("data/file.xlsx", bucket_name="my-bucket")
    """
    if bucket_name:
        # Read from GCS
        return read_xlsx_from_gcs(bucket_name, file_path, credentials_path)
    else:
        # Read from local filesystem
        try:
            df = pd.read_excel(file_path)
            print(f"✓ Successfully read XLSX file from local path: {file_path}")
            print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            return df
        except Exception as e:
            print(f"✗ Error reading local XLSX file: {e}")
            raise


# Example usage for Cloud Run service
if __name__ == '__main__':
    # Example 1: Read from GCS
    bucket_name = "edeliverydata"  # Replace with your bucket name
    file_path = "edeliverydata/eDelivery_AIeDelivery_Database_V1.xlsx"  # Replace with your file path

    try:
        dataframe = read_xlsx_from_gcs(bucket_name, file_path)
        print("\nFirst few rows:")
        print(dataframe.head())
        # Process your dataframe here
    except Exception as e:
        print(f"Failed to read XLSX file: {e}")

    # Example 2: Read from local or GCS based on environment
    # Useful for development (local) vs production (GCS)
    use_gcs = os.getenv('USE_GCS', 'false').lower() == 'true'
    bucket = os.getenv('GCS_BUCKET_NAME') if use_gcs else None

    try:
        df = read_xlsx_from_local_or_gcs(
            file_path="data/spreadsheet.xlsx",
            bucket_name=bucket
        )
        print(f"\nLoaded {len(df)} rows from {'GCS' if use_gcs else 'local filesystem'}")
    except Exception as e:
        print(f"Failed: {e}")
