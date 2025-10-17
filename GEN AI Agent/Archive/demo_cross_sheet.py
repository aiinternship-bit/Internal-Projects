#!/usr/bin/env python3
"""
Cross-Sheet Query Demo
Demonstrates cross-sheet retrieval capabilities
"""
from src.query_engine import QueryEngine
from src.cross_sheet_query import CrossSheetQueryEngine
from src.llm_layer import LLMLayer


def demo_standard_query():
    """
    Demo: Standard query (can retrieve from multiple sheets)
    """
    print("\n" + "=" * 70)
    print("DEMO 1: STANDARD CROSS-SHEET QUERY")
    print("=" * 70)
    print("\nQuery: 'What is the serial number and cost for product xyz?'")
    print("\nHow it works:")
    print("  1. Structure DB finds relevant sheets (Products, Pricing)")
    print("  2. Content DB searches ALL relevant sheets simultaneously")
    print("  3. Returns top-5 results (mixed from all sheets)")
    print("  4. LLM synthesizes answer from combined context")

    try:
        engine = QueryEngine()
        llm = LLMLayer(model_name="mock")

        query = "What is the serial number and cost for product xyz?"
        results = engine.query(
            query,
            top_k_structure=5,
            top_k_content=10
        )

        print(f"\n✓ Retrieved {len(results['structure_results'])} sheets:")
        for struct in results["structure_results"]:
            print(f"  • {struct['sheet']}")

        print(f"\n✓ Retrieved {len(results['content_results'])} content rows")

        # Group by sheet
        by_sheet = {}
        for r in results["content_results"]:
            sheet = r["sheet"]
            if sheet not in by_sheet:
                by_sheet[sheet] = 0
            by_sheet[sheet] += 1

        print(f"  Distribution across sheets:")
        for sheet, count in by_sheet.items():
            print(f"    - {sheet}: {count} rows")

        response = llm.generate_answer(results["context"], query)
        print(f"\n✓ LLM Answer:\n  {response['answer'][:200]}...")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  (Database needs to be built first)")


def demo_enhanced_cross_sheet():
    """
    Demo: Enhanced cross-sheet query with entity focus
    """
    print("\n" + "=" * 70)
    print("DEMO 2: ENHANCED CROSS-SHEET QUERY (Entity-Focused)")
    print("=" * 70)
    print("\nQuery: 'What is the serial number and cost for product xyz?'")
    print("Entity: 'product xyz'")
    print("\nEnhancements:")
    print("  1. Retrieves N results PER sheet (balanced coverage)")
    print("  2. Boosts results containing 'product xyz'")
    print("  3. Provides per-sheet breakdown")
    print("  4. Better for specific entity queries")

    try:
        engine = CrossSheetQueryEngine()
        llm = LLMLayer(model_name="mock")

        query = "What is the serial number and cost for product xyz?"
        results = engine.query_with_joins(
            query,
            entity_identifier="product xyz",
            top_k_structure=5,
            top_k_per_sheet=3
        )

        print(f"\n✓ Retrieved {len(results['structure_results'])} sheets:")
        for struct in results["structure_results"]:
            print(f"  • {struct['sheet']}")

        print(f"\n✓ Per-sheet results (3 per sheet):")
        for sheet, sheet_results in results["per_sheet_results"].items():
            entity_matches = sum(1 for r in sheet_results if r.get("entity_match"))
            print(f"  • {sheet}: {len(sheet_results)} results ({entity_matches} entity matches)")

        response = llm.generate_answer(results["context"], query)
        print(f"\n✓ LLM Answer:\n  {response['answer'][:200]}...")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  (Database needs to be built first)")


def demo_comparison():
    """
    Demo: Visual comparison of both approaches
    """
    print("\n" + "=" * 70)
    print("COMPARISON: STANDARD vs ENHANCED")
    print("=" * 70)

    print("\n┌─────────────────────────┬──────────────────┬──────────────────┐")
    print("│ Feature                 │ Standard Query   │ Enhanced Query   │")
    print("├─────────────────────────┼──────────────────┼──────────────────┤")
    print("│ Sheets searched         │ Multiple (top-k) │ Multiple (top-k) │")
    print("│ Result distribution     │ Global top-k     │ Per-sheet top-k  │")
    print("│ Entity boosting         │ No               │ Yes (1.5x)       │")
    print("│ Per-sheet breakdown     │ No               │ Yes              │")
    print("│ Best for                │ General queries  │ Entity queries   │")
    print("│ Example query           │ 'delivery data'  │ 'order #12345'   │")
    print("└─────────────────────────┴──────────────────┴──────────────────┘")


def demo_cli_usage():
    """
    Demo: Show CLI usage examples
    """
    print("\n" + "=" * 70)
    print("CLI USAGE EXAMPLES")
    print("=" * 70)

    print("\n1. Standard cross-sheet query:")
    print("   python main.py query \"What is the cost and serial for product xyz?\"")

    print("\n2. Enhanced cross-sheet query:")
    print("   python main.py query \"What is the cost and serial for product xyz?\" \\")
    print("     --cross-sheet --entity \"product xyz\"")

    print("\n3. With more results per sheet:")
    print("   python main.py query \"What is the cost and serial for product xyz?\" \\")
    print("     --cross-sheet --entity \"product xyz\" \\")
    print("     --top-k-structure 7 --top-k-content 5")

    print("\n4. With real LLM:")
    print("   python main.py query \"What is the cost and serial for product xyz?\" \\")
    print("     --cross-sheet --entity \"product xyz\" \\")
    print("     --llm gpt-3.5-turbo")


def demo_python_api():
    """
    Demo: Show Python API usage
    """
    print("\n" + "=" * 70)
    print("PYTHON API EXAMPLES")
    print("=" * 70)

    print("\n# Standard cross-sheet query")
    print("""
from src.query_engine import QueryEngine
from src.llm_layer import LLMLayer

engine = QueryEngine()
llm = LLMLayer(model_name="gpt-3.5-turbo")

results = engine.query(
    "What is the serial number and cost for product xyz?",
    top_k_structure=5,
    top_k_content=10
)

response = llm.generate_answer(results["context"], results["query"])
print(response["answer"])
""")

    print("\n# Enhanced cross-sheet query with entity focus")
    print("""
from src.cross_sheet_query import CrossSheetQueryEngine
from src.llm_layer import LLMLayer

engine = CrossSheetQueryEngine()
llm = LLMLayer(model_name="gpt-3.5-turbo")

results = engine.query_with_joins(
    "What is the serial number and cost for product xyz?",
    entity_identifier="product xyz",
    top_k_structure=5,
    top_k_per_sheet=3
)

# See per-sheet breakdown
for sheet, sheet_results in results["per_sheet_results"].items():
    print(f"{sheet}: {len(sheet_results)} results")

response = llm.generate_answer(results["context"], results["query"])
print(response["answer"])
""")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("CROSS-SHEET QUERY DEMONSTRATION")
    print("=" * 70)
    print("\nThis demonstrates how Excel-RAG handles queries spanning multiple sheets.")
    print("The system can retrieve data from different sheets and combine them")
    print("for the LLM to synthesize a comprehensive answer.")

    demo_standard_query()
    demo_enhanced_cross_sheet()
    demo_comparison()
    demo_cli_usage()
    demo_python_api()

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("\n✓ YES - The system CAN handle cross-sheet queries!")
    print("✓ Standard mode: Fast, good for general queries")
    print("✓ Enhanced mode: Better coverage for specific entities")
    print("✓ Both modes: Search multiple sheets simultaneously")
    print("✓ LLM combines information across sheets")
    print("\n✗ Limitation: Semantic retrieval, not SQL-style foreign key joins")
    print("✗ Works best when entity names are consistent across sheets")
    print("\n📖 For more details, see: CROSS_SHEET_GUIDE.md")
    print()


if __name__ == "__main__":
    main()
