#!/usr/bin/env python3
"""
Query Milvus Database with GCS Download Support
Downloads Milvus database from GCS at runtime if needed, then performs queries
This is the pattern to use in Cloud Run deployments
"""
import argparse
import os
from src.query_engine import QueryEngine
from src.llm_layer import LLMLayer
from src.milvus_gcs_utils import ensure_milvus_available
from src import config


def initialize_from_gcs(
    local_db_path: str = config.DB_PATH,
    bucket_name: str = "edeliverydata",
    gcs_db_path: str = "milvus_edelivery.db",
    force_download: bool = False
) -> bool:
    """
    Initialize Milvus database from GCS.
    Downloads from GCS if not available locally.

    Args:
        local_db_path: Local path to store/use Milvus database
        bucket_name: GCS bucket name containing the database
        gcs_db_path: Path to database file in GCS bucket
        force_download: Force download even if local copy exists

    Returns:
        bool: True if database is ready, False otherwise
    """
    print("\n" + "="*80)
    print("INITIALIZING MILVUS DATABASE FROM GCS")
    print("="*80)

    success = ensure_milvus_available(
        local_db_path=local_db_path,
        bucket_name=bucket_name,
        gcs_file_path=gcs_db_path,
        force_download=force_download
    )

    if success:
        print("\n✅ Milvus database is ready for querying!")
        print("="*80)
        return True
    else:
        print("\n❌ Failed to initialize Milvus database from GCS")
        print("="*80)
        return False


def run_query(
    query: str,
    db_path: str = config.DB_PATH,
    llm_model: str = config.LLM_MODEL,
    top_k_structure: int = config.TOP_K_STRUCTURE,
    top_k_content: int = config.TOP_K_CONTENT
):
    """
    Run a query through the complete RAG pipeline.

    Args:
        query: User question
        db_path: Path to Milvus database
        llm_model: LLM model to use
        top_k_structure: Number of structure results
        top_k_content: Number of content results
    """
    print("\n" + "="*80)
    print("EDELIVERY RAG QUERY")
    print("="*80)
    print(f"Query: {query}")
    print("="*80)

    # Initialize query engine
    try:
        engine = QueryEngine(db_path)
        results = engine.query(query, top_k_structure, top_k_content)
    except Exception as e:
        print(f"\n✗ Error executing query: {e}")
        import traceback
        traceback.print_exc()
        return

    # Display retrieval results
    print("\n--- RETRIEVED STRUCTURE ---")
    for i, struct in enumerate(results["structure_results"], 1):
        print(f"{i}. {struct['sheet']} (score: {struct['score']:.4f})")

    print("\n--- RETRIEVED CONTENT (Top 5) ---")
    for i, content in enumerate(results["content_results"][:5], 1):
        preview = content["text"][:100]
        print(f"{i}. [{content['sheet']}] {preview}... (score: {content['score']:.4f})")

    # Generate LLM answer
    print("\n--- GENERATING ANSWER ---")
    try:
        llm = LLMLayer(model_name=llm_model)
        response = llm.generate_answer(results["context"], query)

        print(f"\nModel: {response['model']} ({response['backend']})")
        print(f"Token usage: {response['token_usage']}")
        print(f"\n--- ANSWER ---")
        print(response["answer"])
    except Exception as e:
        print(f"\n✗ Error generating LLM answer: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)


def interactive_mode(
    db_path: str = config.DB_PATH,
    llm_model: str = config.LLM_MODEL
):
    """
    Interactive query mode.

    Args:
        db_path: Path to Milvus database
        llm_model: LLM model to use
    """
    print("\n" + "="*80)
    print("EDELIVERY RAG INTERACTIVE MODE")
    print("="*80)
    print("Enter queries to search the eDelivery database.")
    print("Type 'exit' or 'quit' to stop.\n")

    try:
        engine = QueryEngine(db_path)
        llm = LLMLayer(model_name=llm_model)
    except Exception as e:
        print(f"✗ Error initializing: {e}")
        return

    while True:
        try:
            # Get user query
            query = input("\nQuery> ").strip()

            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not query:
                continue

            # Execute query
            print("\nSearching...")
            results = engine.query(query)

            # Generate answer
            response = llm.generate_answer(results["context"], query)

            # Display answer
            print(f"\n{response['answer']}\n")
            print(f"[Retrieved from {len(results['structure_results'])} sheets, "
                  f"{len(results['content_results'])} rows | "
                  f"Tokens: {response['token_usage']}]\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="Query eDelivery Milvus database (with GCS download support)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init command - download database from GCS
    init_parser = subparsers.add_parser("init", help="Initialize database from GCS")
    init_parser.add_argument(
        "--bucket",
        default="edeliverydata",
        help="GCS bucket name (default: edeliverydata)"
    )
    init_parser.add_argument(
        "--gcs-db-path",
        default="milvus_edelivery.db",
        help="Path to database in GCS bucket (default: milvus_edelivery.db)"
    )
    init_parser.add_argument(
        "--local-db",
        default=config.DB_PATH,
        help=f"Local path to store database (default: {config.DB_PATH})"
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Force download even if local copy exists"
    )

    # Query command
    query_parser = subparsers.add_parser("query", help="Run a single query")
    query_parser.add_argument(
        "question",
        help="Question to ask"
    )
    query_parser.add_argument(
        "--db",
        default=config.DB_PATH,
        help=f"Path to Milvus database (default: {config.DB_PATH})"
    )
    query_parser.add_argument(
        "--llm",
        default=config.LLM_MODEL,
        help=f"LLM model to use (default: {config.LLM_MODEL})"
    )
    query_parser.add_argument(
        "--init-from-gcs",
        action="store_true",
        help="Initialize database from GCS before querying"
    )
    query_parser.add_argument(
        "--bucket",
        default="edeliverydata",
        help="GCS bucket name (if --init-from-gcs is used)"
    )
    query_parser.add_argument(
        "--gcs-db-path",
        default="milvus_edelivery.db",
        help="Path to database in GCS bucket (if --init-from-gcs is used)"
    )

    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Interactive query mode")
    interactive_parser.add_argument(
        "--db",
        default=config.DB_PATH,
        help=f"Path to Milvus database (default: {config.DB_PATH})"
    )
    interactive_parser.add_argument(
        "--llm",
        default=config.LLM_MODEL,
        help=f"LLM model to use (default: {config.LLM_MODEL})"
    )
    interactive_parser.add_argument(
        "--init-from-gcs",
        action="store_true",
        help="Initialize database from GCS before starting"
    )
    interactive_parser.add_argument(
        "--bucket",
        default="edeliverydata",
        help="GCS bucket name (if --init-from-gcs is used)"
    )
    interactive_parser.add_argument(
        "--gcs-db-path",
        default="milvus_edelivery.db",
        help="Path to database in GCS bucket (if --init-from-gcs is used)"
    )

    args = parser.parse_args()

    # Execute command
    if args.command == "init":
        success = initialize_from_gcs(
            local_db_path=args.local_db,
            bucket_name=args.bucket,
            gcs_db_path=args.gcs_db_path,
            force_download=args.force
        )
        exit(0 if success else 1)

    elif args.command == "query":
        # Initialize from GCS if requested
        if args.init_from_gcs:
            success = initialize_from_gcs(
                local_db_path=args.db,
                bucket_name=args.bucket,
                gcs_db_path=args.gcs_db_path
            )
            if not success:
                print("Failed to initialize database from GCS")
                exit(1)

        run_query(args.question, args.db, args.llm)

    elif args.command == "interactive":
        # Initialize from GCS if requested
        if args.init_from_gcs:
            success = initialize_from_gcs(
                local_db_path=args.db,
                bucket_name=args.bucket,
                gcs_db_path=args.gcs_db_path
            )
            if not success:
                print("Failed to initialize database from GCS")
                exit(1)

        interactive_mode(args.db, args.llm)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
