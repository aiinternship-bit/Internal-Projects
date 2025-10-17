#!/usr/bin/env python3
"""
Example Usage Script
Demonstrates how to use the Excel-RAG system programmatically
"""
from src.structure_db import StructureVectorDB
from src.content_db import ContentVectorDB
from src.query_engine import QueryEngine
from src.llm_layer import LLMLayer
from src.testing import ExcelRAGTester
from src import config


def example_build_databases():
    """Example: Build databases from Excel file"""
    print("\n=== EXAMPLE 1: Building Databases ===\n")

    excel_path = "eDelivery_AIeDelivery_Database_V1.xlsx"

    # Build structure database
    print("Building structure database...")
    structure_db = StructureVectorDB()
    structure_db.build_from_excel(excel_path, drop_existing=True)

    # Build content database (warning: takes hours for large files)
    print("\nBuilding content database (this may take a while)...")
    content_db = ContentVectorDB()
    content_db.build_from_excel(excel_path, drop_existing=True)

    print("\nDatabases built successfully!")


def example_query_structure():
    """Example: Query just the structure database"""
    print("\n=== EXAMPLE 2: Querying Structure ===\n")

    structure_db = StructureVectorDB()

    query = "customer delivery information"
    print(f"Query: '{query}'")

    results = structure_db.search(query, top_k=5)

    print(f"\nFound {len(results)} relevant sheets:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['sheet']}")
        print(f"   Columns: {result['columns'][:100]}...")
        print(f"   Score: {result['score']:.4f}\n")


def example_query_content():
    """Example: Query the content database"""
    print("\n=== EXAMPLE 3: Querying Content ===\n")

    content_db = ContentVectorDB()

    query = "digital delivery system"
    print(f"Query: '{query}'")

    # Option 1: Search all sheets
    print("\nSearching all sheets...")
    results = content_db.search(query, top_k=3)

    print(f"\nTop {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['sheet']}]")
        print(f"   {result['text'][:150]}...")
        print(f"   Score: {result['score']:.4f}\n")

    # Option 2: Search specific sheets only
    print("\nSearching specific sheets...")
    results = content_db.search(
        query,
        top_k=3,
        sheet_filter=["Deliveries", "Customers"]
    )

    print(f"\nFiltered results: {len(results)}\n")


def example_dual_vector_query():
    """Example: Use query engine for dual-vector retrieval"""
    print("\n=== EXAMPLE 4: Dual-Vector Retrieval ===\n")

    engine = QueryEngine()

    query = "What are the delivery statuses?"
    print(f"Query: '{query}'")

    # Execute dual-stage retrieval
    results = engine.query(
        query,
        top_k_structure=3,
        top_k_content=5
    )

    print(f"\n--- Structure Results ---")
    for struct in results["structure_results"]:
        print(f"  • {struct['sheet']} (score: {struct['score']:.4f})")

    print(f"\n--- Content Results ---")
    for content in results["content_results"]:
        preview = content["text"][:80]
        print(f"  • [{content['sheet']}] {preview}... (score: {content['score']:.4f})")

    print(f"\n--- Context for LLM ---")
    print(results["context"][:500])
    print("...\n")


def example_llm_integration():
    """Example: Generate answers with LLM"""
    print("\n=== EXAMPLE 5: LLM Integration ===\n")

    # First, get context from query engine
    engine = QueryEngine()
    query = "How many deliveries are there?"
    results = engine.query(query)

    # Then, use LLM to generate answer
    llm = LLMLayer(model_name="mock")  # Use "gpt-3.5-turbo" for real LLM

    response = llm.generate_answer(results["context"], query)

    print(f"Query: '{query}'")
    print(f"\nModel: {response['model']} ({response['backend']})")
    print(f"Token usage: {response['token_usage']}")
    print(f"\nAnswer:\n{response['answer']}\n")


def example_custom_llm():
    """Example: Using different LLM backends"""
    print("\n=== EXAMPLE 6: Custom LLM Backend ===\n")

    sample_context = "Sheet: Sales, Data: Q1 Revenue: $1M, Q2 Revenue: $1.2M"
    query = "What was the Q1 revenue?"

    # Mock LLM (no API needed)
    print("1. Mock LLM (for testing):")
    mock_llm = LLMLayer(model_name="mock")
    response = mock_llm.generate_answer(sample_context, query)
    print(f"   Answer: {response['answer'][:100]}...\n")

    # OpenAI GPT (requires API key)
    print("2. OpenAI GPT (requires OPENAI_API_KEY):")
    print("   export OPENAI_API_KEY='your-key'")
    print("   llm = LLMLayer(model_name='gpt-3.5-turbo')")
    print("   response = llm.generate_answer(context, query)\n")

    # Anthropic Claude (requires API key)
    print("3. Anthropic Claude (requires ANTHROPIC_API_KEY):")
    print("   export ANTHROPIC_API_KEY='your-key'")
    print("   llm = LLMLayer(model_name='claude-3-sonnet-20240229')")
    print("   response = llm.generate_answer(context, query)\n")


def example_testing():
    """Example: Running tests"""
    print("\n=== EXAMPLE 7: Running Tests ===\n")

    tester = ExcelRAGTester()

    # Run individual tests
    print("Running connectivity test...")
    tester.test_connectivity()

    print("\nRunning embedding test...")
    tester.test_embedding("sample query")

    print("\nRunning retrieval test...")
    tester.test_retrieval("digital delivery")

    # Or run all tests at once
    print("\n\nRunning full test suite...")
    results = tester.run_all_tests("digital delivery system")


def example_advanced_query():
    """Example: Advanced query with custom parameters"""
    print("\n=== EXAMPLE 8: Advanced Query ===\n")

    engine = QueryEngine()

    # Query with custom top-k values
    query = "customer satisfaction scores"

    results = engine.query(
        query,
        top_k_structure=5,  # Get more sheet options
        top_k_content=10    # Get more data rows
    )

    print(f"Query: '{query}'")
    print(f"Retrieved {len(results['structure_results'])} sheets")
    print(f"Retrieved {len(results['content_results'])} rows\n")

    # Use custom LLM settings
    llm = LLMLayer(
        model_name="mock",
        temperature=0.3,  # Lower temperature for more focused answers
        max_tokens=500
    )

    response = llm.generate_answer(results["context"], query)
    print(f"Answer:\n{response['answer']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("EXCEL-RAG SYSTEM - EXAMPLE USAGE")
    print("=" * 60)

    examples = [
        # ("Build Databases", example_build_databases),  # Commented - takes hours
        ("Query Structure", example_query_structure),
        ("Query Content", example_query_content),
        ("Dual-Vector Retrieval", example_dual_vector_query),
        ("LLM Integration", example_llm_integration),
        ("Custom LLM Backend", example_custom_llm),
        ("Running Tests", example_testing),
        ("Advanced Query", example_advanced_query),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
            print("(This is expected if databases are not built yet)\n")

    print("\n" + "=" * 60)
    print("EXAMPLES COMPLETE")
    print("=" * 60)
    print("\nTo build databases first, run:")
    print("  python main.py build --excel eDelivery_AIeDelivery_Database_V1.xlsx --drop")
    print("\nFor more info, see README.md or run:")
    print("  python main.py --help")
    print()


if __name__ == "__main__":
    main()
