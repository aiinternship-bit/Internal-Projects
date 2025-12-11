"""
Vector Database Ingestion Script
Processes JSON files and loads them into ChromaDB for RAG retrieval
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from vector_db_schema import PrinterVectorSchema, PrinterDocument
import argparse


class VectorDBIngestion:
    """Handles ingestion of printer specifications into vector database."""

    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "printer_specs"):
        """
        Initialize vector database connection.

        Args:
            db_path: Path to ChromaDB storage directory
            collection_name: Name of the collection to use
        """
        self.db_path = db_path
        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)

        # Use sentence transformers for embeddings (free, local)
        # Uses HF_TOKEN environment variable if available
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2",  # Fast, efficient, 384-dimensional embeddings
            model_kwargs={'token': os.environ.get('HF_TOKEN')}
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Zebra printer specifications for RAG"}
        )

        print(f"Connected to ChromaDB at {db_path}")
        print(f"Collection: {collection_name}")
        print(f"Document count: {self.collection.count()}")

    def ingest_json_file(self, json_path: str) -> int:
        """
        Ingest a single JSON file into the vector database.

        Args:
            json_path: Path to JSON file

        Returns:
            Number of chunks inserted
        """
        print(f"\nProcessing: {json_path}")

        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert to chunks
        chunks = PrinterVectorSchema.extract_chunks_from_json(data)

        if not chunks:
            print(f"  No chunks generated for {json_path}")
            return 0

        # Prepare data for ChromaDB
        ids = [chunk.doc_id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        # Insert into ChromaDB (will auto-generate embeddings)
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        print(f"  Inserted {len(chunks)} chunks for model: {data.get('product_info', {}).get('model', 'UNKNOWN')}")

        return len(chunks)

    def ingest_directory(self, directory: str) -> Dict[str, int]:
        """
        Ingest all JSON files from a directory.

        Args:
            directory: Path to directory containing JSON files

        Returns:
            Dictionary with statistics
        """
        directory_path = Path(directory)
        json_files = sorted(directory_path.glob("*.json"))

        if not json_files:
            print(f"No JSON files found in {directory}")
            return {"total_files": 0, "total_chunks": 0}

        print(f"Found {len(json_files)} JSON files to ingest\n")

        total_chunks = 0
        successful_files = 0

        for json_file in json_files:
            try:
                chunks_count = self.ingest_json_file(str(json_file))
                total_chunks += chunks_count
                successful_files += 1
            except Exception as e:
                print(f"  Error processing {json_file}: {e}")
                import traceback
                traceback.print_exc()
                continue

        stats = {
            "total_files": len(json_files),
            "successful_files": successful_files,
            "total_chunks": total_chunks,
            "final_document_count": self.collection.count()
        }

        print(f"\n{'='*80}")
        print("Ingestion Complete")
        print(f"{'='*80}")
        print(f"Files processed: {successful_files}/{len(json_files)}")
        print(f"Total chunks inserted: {total_chunks}")
        print(f"Total documents in DB: {self.collection.count()}")
        print(f"{'='*80}\n")

        return stats

    def clear_collection(self):
        """Clear all documents from the collection."""
        # Delete and recreate collection
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Zebra printer specifications for RAG"}
        )
        print(f"Collection '{self.collection_name}' cleared")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.collection.count()

        if count == 0:
            return {"document_count": 0}

        # Get a sample to understand data
        sample = self.collection.peek(limit=10)

        # Count unique printers
        unique_models = set()
        chunk_types = {}

        if sample and sample.get('metadatas'):
            for metadata in sample['metadatas']:
                if metadata.get('model'):
                    unique_models.add(metadata['model'])
                if metadata.get('chunk_type'):
                    chunk_type = metadata['chunk_type']
                    chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1

        return {
            "document_count": count,
            "unique_models_sample": len(unique_models),
            "chunk_types_sample": chunk_types
        }

    def query_test(self, query: str, n_results: int = 3):
        """
        Test query to verify embeddings are working.

        Args:
            query: Test query string
            n_results: Number of results to return
        """
        print(f"\nTest Query: '{query}'")
        print(f"{'='*80}")

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if results and results['documents']:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                print(f"\nResult {i}:")
                print(f"  Model: {metadata.get('model', 'N/A')}")
                print(f"  Chunk Type: {metadata.get('chunk_type', 'N/A')}")
                print(f"  Distance: {distance:.4f}")
                print(f"  Content Preview: {doc[:200]}...")
                print(f"  {'='*80}")
        else:
            print("No results found")


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Ingest printer specification JSON files into ChromaDB"
    )
    parser.add_argument(
        "input",
        help="Input JSON file or directory containing JSON files"
    )
    parser.add_argument(
        "--db-path",
        default="./chroma_db",
        help="Path to ChromaDB storage directory (default: ./chroma_db)"
    )
    parser.add_argument(
        "--collection",
        default="printer_specs",
        help="Collection name (default: printer_specs)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing collection before ingesting"
    )
    parser.add_argument(
        "--test-query",
        help="Run a test query after ingestion"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show collection statistics"
    )

    args = parser.parse_args()

    # Initialize ingestion
    ingestion = VectorDBIngestion(
        db_path=args.db_path,
        collection_name=args.collection
    )

    # Clear if requested
    if args.clear:
        print("Clearing existing collection...")
        ingestion.clear_collection()

    # Show stats if requested
    if args.stats:
        stats = ingestion.get_collection_stats()
        print("\nCollection Statistics:")
        print(json.dumps(stats, indent=2))
        return 0

    # Ingest data
    input_path = Path(args.input)

    if input_path.is_file():
        ingestion.ingest_json_file(str(input_path))
    elif input_path.is_dir():
        ingestion.ingest_directory(str(input_path))
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        return 1

    # Run test query if provided
    if args.test_query:
        ingestion.query_test(args.test_query)

    return 0


if __name__ == "__main__":
    exit(main())
