#!/usr/bin/env python3
"""
Excel-RAG Main Entry Point
Complete pipeline for Excel data retrieval and LLM-based Q&A
"""
import argparse
from pathlib import Path
from src.structure_db import StructureVectorDB
from src.content_db import ContentVectorDB
from src.query_engine import QueryEngine
from src.cross_sheet_query import CrossSheetQueryEngine
from src.llm_layer import LLMLayer
from src.testing import ExcelRAGTester
from src import config


def build_databases(excel_path: str, db_path: str = config.DB_PATH, drop_existing: bool = False):
    """
    Build both structure and content databases from Excel file

    Args:
        excel_path: Path to Excel file
        db_path: Path to Milvus database
        drop_existing: Whether to drop existing collections
    """
    print("\n" + "=" * 60)
    print("BUILDING VECTOR DATABASES")
    print("=" * 60)

    # Build structure database
    print("\n[1/2] Building Structure Database...")
    structure_db = StructureVectorDB(db_path)
    structure_db.build_from_excel(excel_path, drop_existing=drop_existing)

    # Build content database
    print("\n[2/2] Building Content Database...")
    print("WARNING: This may take several hours for large files!")
    content_db = ContentVectorDB(db_path)
    content_db.build_from_excel(excel_path, drop_existing=drop_existing)

    print("\n" + "=" * 60)
    print("DATABASE BUILD COMPLETE!")
    print("=" * 60)


def run_query(
    query: str,
    db_path: str = config.DB_PATH,
    llm_model: str = config.LLM_MODEL,
    top_k_structure: int = config.TOP_K_STRUCTURE,
    top_k_content: int = config.TOP_K_CONTENT,
    entity: str = None,
    cross_sheet: bool = False
):
    """
    Run a query through the complete RAG pipeline

    Args:
        query: User question
        db_path: Path to Milvus database
        llm_model: LLM model to use
        top_k_structure: Number of structure results
        top_k_content: Number of content results
        entity: Optional entity identifier for cross-sheet queries
        cross_sheet: Use enhanced cross-sheet engine
    """
    print("\n" + "=" * 60)
    print("EXCEL-RAG QUERY" + (" (CROSS-SHEET MODE)" if cross_sheet else ""))
    print("=" * 60)

    # Initialize query engine
    if cross_sheet:
        engine = CrossSheetQueryEngine(db_path)
        if entity:
            results = engine.query_with_joins(
                query,
                entity_identifier=entity,
                top_k_structure=top_k_structure,
                top_k_per_sheet=top_k_content
            )
        else:
            results = engine.query(query, top_k_structure, top_k_content)
    else:
        engine = QueryEngine(db_path)
        results = engine.query(query, top_k_structure, top_k_content)

    # Display retrieval results
    print("\n--- RETRIEVED STRUCTURE ---")
    for i, struct in enumerate(results["structure_results"], 1):
        print(f"{i}. {struct['sheet']} (score: {struct['score']:.4f})")

    print("\n--- RETRIEVED CONTENT ---")
    if cross_sheet and "per_sheet_results" in results:
        for sheet, sheet_results in results["per_sheet_results"].items():
            print(f"\n{sheet}: {len(sheet_results)} results")
            for i, content in enumerate(sheet_results, 1):
                preview = content["text"][:80]
                entity_mark = " [*]" if content.get("entity_match") else ""
                print(f"  {i}. {preview}...{entity_mark} (score: {content['score']:.4f})")
    else:
        for i, content in enumerate(results["content_results"], 1):
            preview = content["text"][:100]
            print(f"{i}. [{content['sheet']}] {preview}... (score: {content['score']:.4f})")

    # Generate LLM answer
    print("\n--- GENERATING ANSWER ---")
    llm = LLMLayer(model_name=llm_model)
    response = llm.generate_answer(results["context"], query)

    print(f"\nModel: {response['model']} ({response['backend']})")
    print(f"Token usage: {response['token_usage']}")
    print(f"\n--- ANSWER ---")
    print(response["answer"])

    print("\n" + "=" * 60)


def run_tests(db_path: str = config.DB_PATH, query: str = "digital delivery system"):
    """
    Run complete test suite

    Args:
        db_path: Path to Milvus database
        query: Sample query for testing
    """
    tester = ExcelRAGTester(db_path)
    tester.run_all_tests(sample_query=query)


def interactive_mode(db_path: str = config.DB_PATH, llm_model: str = config.LLM_MODEL):
    """
    Interactive query mode

    Args:
        db_path: Path to Milvus database
        llm_model: LLM model to use
    """
    print("\n" + "=" * 60)
    print("EXCEL-RAG INTERACTIVE MODE")
    print("=" * 60)
    print("Enter queries to search the Excel database.")
    print("Type 'exit' or 'quit' to stop.\n")

    engine = QueryEngine(db_path)
    llm = LLMLayer(model_name=llm_model)

    while True:
        try:
            # Get user query
            query = input("Query> ").strip()

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
        description="Excel-RAG: Vector-based retrieval and LLM Q&A over Excel data"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build vector databases from Excel")
    build_parser.add_argument(
        "--excel",
        default=config.EXCEL_FILE,
        help="Path to Excel file"
    )
    build_parser.add_argument(
        "--db",
        default=config.DB_PATH,
        help="Path to Milvus database"
    )
    build_parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing collections"
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
        help="Path to Milvus database"
    )
    query_parser.add_argument(
        "--llm",
        default=config.LLM_MODEL,
        help=f"LLM model to use (default: auto-detected = {config.LLM_MODEL})"
    )
    query_parser.add_argument(
        "--top-k-structure",
        type=int,
        default=config.TOP_K_STRUCTURE,
        help="Number of structure results"
    )
    query_parser.add_argument(
        "--top-k-content",
        type=int,
        default=config.TOP_K_CONTENT,
        help="Number of content results"
    )
    query_parser.add_argument(
        "--entity",
        help="Entity identifier for cross-sheet queries (e.g., 'product xyz')"
    )
    query_parser.add_argument(
        "--cross-sheet",
        action="store_true",
        help="Use enhanced cross-sheet query engine"
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Run test suite")
    test_parser.add_argument(
        "--db",
        default=config.DB_PATH,
        help="Path to Milvus database"
    )
    test_parser.add_argument(
        "--query",
        default="digital delivery system",
        help="Sample query for testing"
    )

    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Interactive query mode")
    interactive_parser.add_argument(
        "--db",
        default=config.DB_PATH,
        help="Path to Milvus database"
    )
    interactive_parser.add_argument(
        "--llm",
        default=config.LLM_MODEL,
        help=f"LLM model to use (default: auto-detected = {config.LLM_MODEL})"
    )

    args = parser.parse_args()

    # Execute command
    if args.command == "build":
        build_databases(args.excel, args.db, args.drop)
    elif args.command == "query":
        run_query(
            args.question,
            args.db,
            args.llm,
            args.top_k_structure,
            args.top_k_content,
            args.entity if hasattr(args, 'entity') else None,
            args.cross_sheet if hasattr(args, 'cross_sheet') else False
        )
    elif args.command == "test":
        run_tests(args.db, args.query)
    elif args.command == "interactive":
        interactive_mode(args.db, args.llm)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
