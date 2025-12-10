#!/usr/bin/env python3
"""
Initialize Vector Databases for Docker Container
Sets up vector databases for both GEN AI Agent (Milvus) and Zebra Project (ChromaDB)
"""
import sys
import os
from pathlib import Path

def init_zebra_chromadb():
    """Initialize Zebra Project ChromaDB with printer specifications"""
    print("\n" + "="*80)
    print("Initializing Zebra Project ChromaDB...")
    print("="*80)

    try:
        # Change to Zebra Project directory
        zebra_dir = Path("/app/Zebra Project")
        os.chdir(zebra_dir)
        sys.path.insert(0, str(zebra_dir / "src"))

        from src.vector_db_ingest import VectorDBIngestion

        # Initialize with container paths
        db_path = str(zebra_dir / "chroma_db")
        json_dir = str(zebra_dir / "output")

        print(f"Database path: {db_path}")
        print(f"JSON directory: {json_dir}")

        # Check if JSON files exist
        json_files = list(Path(json_dir).glob("*.json"))
        if not json_files:
            print(f"⚠️  No JSON files found in {json_dir}")
            print("Skipping Zebra ChromaDB initialization")
            return False

        print(f"Found {len(json_files)} JSON files to process")

        # Create ingestion instance and load data
        ingestion = VectorDBIngestion(db_path=db_path)

        # Clear existing and ingest
        ingestion.clear_collection()
        stats = ingestion.ingest_directory(json_dir)

        print(f"\n✅ Zebra ChromaDB initialized successfully!")
        print(f"   Total documents: {stats['final_document_count']}")
        print(f"   Files processed: {stats['successful_files']}/{stats['total_files']}")

        return True

    except Exception as e:
        print(f"❌ Error initializing Zebra ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        return False


def init_gen_ai_milvus():
    """Initialize GEN AI Agent Milvus with Excel data"""
    print("\n" + "="*80)
    print("Initializing GEN AI Agent Milvus...")
    print("="*80)

    try:
        # Change to GEN AI Agent directory
        gen_ai_dir = Path("/app/GEN AI Agent/Archive")
        os.chdir(gen_ai_dir)
        sys.path.insert(0, str(gen_ai_dir / "src"))

        from src.content_db import ContentVectorDB
        from src.structure_db import StructureVectorDB
        from src import config
        from src.gcs_utils import read_xlsx_from_local_or_gcs

        db_path = str(gen_ai_dir / "milvus_edelivery.db")

        # Check for GCS configuration
        use_gcs = os.environ.get('USE_GCS', 'false').lower() == 'true'
        bucket_name = os.environ.get('GCS_BUCKET_NAME') if use_gcs else None

        if use_gcs and bucket_name:
            print(f"Using GCS bucket: {bucket_name}")
            file_path = os.environ.get('GCS_FILE_PATH', 'edeliverydata/eDelivery_AIeDelivery_Database_V1.xlsx')
            excel_path = file_path
        else:
            print("Using local Excel file")
            excel_path = str(gen_ai_dir / "eDelivery_AIeDelivery_Database_V1.xlsx")
            bucket_name = None

            # Check if local file exists
            if not Path(excel_path).exists():
                print(f"⚠️  Excel file not found: {excel_path}")
                print("Skipping GEN AI Milvus initialization")
                return False

        print(f"Database path: {db_path}")
        print(f"Excel path: {excel_path}")

        # Initialize databases
        content_db = ContentVectorDB(db_path=db_path)
        structure_db = StructureVectorDB(db_path=db_path)

        # Build structure database (lightweight, always runs)
        print("\n📊 Building Structure Database...")
        if bucket_name:
            # Read from GCS
            df = read_xlsx_from_local_or_gcs(excel_path, bucket_name=bucket_name)
            # For structure DB, we need to pass the dataframe
            structure_db.create_collection(drop_existing=True)
            # Extract structure from sheets
            import pandas as pd
            all_sheets = pd.read_excel(excel_path, sheet_name=None) if not bucket_name else {sheet: df for sheet in [df.name] if hasattr(df, 'name')}
            structure_df = structure_db.extract_structure_from_excel_sheets(all_sheets)
            structure_db.insert_structure_batched(structure_df)
        else:
            structure_db.build_from_excel(excel_path, drop_existing=True)

        # Build content database (heavy, only if not exists or forced)
        print("\n📄 Building Content Database...")
        if bucket_name:
            df = read_xlsx_from_local_or_gcs(excel_path, bucket_name=bucket_name)
            # Save temporarily for content_db processing
            temp_path = "/tmp/edelivery_temp.xlsx"
            df.to_excel(temp_path, index=False)
            content_db.build_from_excel(temp_path, drop_existing=True)
            os.remove(temp_path)
        else:
            content_db.build_from_excel(excel_path, drop_existing=True)

        print(f"\n✅ GEN AI Milvus initialized successfully!")
        print(f"   Database: {db_path}")

        return True

    except Exception as e:
        print(f"❌ Error initializing GEN AI Milvus: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main initialization routine"""
    print("\n" + "="*80)
    print("VECTOR DATABASE INITIALIZATION")
    print("="*80)

    results = {
        'zebra': False,
        'gen_ai': False
    }

    # Initialize Zebra ChromaDB
    results['zebra'] = init_zebra_chromadb()

    # Initialize GEN AI Milvus
    results['gen_ai'] = init_gen_ai_milvus()

    # Summary
    print("\n" + "="*80)
    print("INITIALIZATION SUMMARY")
    print("="*80)
    print(f"Zebra Project ChromaDB: {'✅ Success' if results['zebra'] else '❌ Failed'}")
    print(f"GEN AI Agent Milvus:    {'✅ Success' if results['gen_ai'] else '❌ Failed'}")
    print("="*80)

    # Exit with error if both failed
    if not any(results.values()):
        print("\n⚠️  Warning: No vector databases were initialized successfully")
        print("The application will still start, but RAG features may not work")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
