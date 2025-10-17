"""
Cross-Sheet Query Enhancement Module
Improves handling of queries spanning multiple sheets
"""
from typing import Dict, Any, List, Optional
from .query_engine import QueryEngine
from .llm_layer import LLMLayer
from . import config


class CrossSheetQueryEngine(QueryEngine):
    """
    Enhanced query engine with better cross-sheet retrieval strategies
    """

    def query_with_joins(
        self,
        user_query: str,
        entity_identifier: Optional[str] = None,
        top_k_structure: int = config.TOP_K_STRUCTURE,
        top_k_per_sheet: int = 3
    ) -> Dict[str, Any]:
        """
        Execute query with enhanced cross-sheet retrieval

        Strategy:
        1. Find relevant sheets
        2. Retrieve top-k results PER SHEET (not globally)
        3. If entity_identifier provided, re-rank by entity match
        4. Combine results for LLM

        Args:
            user_query: User's natural language query
            entity_identifier: Optional specific entity to focus on (e.g., "product xyz")
            top_k_structure: Number of sheets to retrieve
            top_k_per_sheet: Number of results per sheet (ensures coverage)

        Returns:
            Enhanced query results with per-sheet breakdown
        """
        print(f"\n[Cross-Sheet Query] Processing: '{user_query}'")
        if entity_identifier:
            print(f"[Cross-Sheet Query] Focusing on entity: '{entity_identifier}'")

        # Step 1: Find relevant sheets
        structure_results = self.structure_db.search(user_query, top_k=top_k_structure)

        if not structure_results:
            return self._empty_result(user_query)

        relevant_sheets = [r["sheet"] for r in structure_results]
        print(f"[Cross-Sheet Query] Relevant sheets: {relevant_sheets}")

        # Step 2: Retrieve from each sheet separately for balanced coverage
        all_content_results = []
        per_sheet_results = {}

        for sheet in relevant_sheets:
            # Search each sheet individually
            sheet_results = self.content_db.search(
                user_query,
                top_k=top_k_per_sheet,
                sheet_filter=[sheet]  # Single sheet at a time
            )

            per_sheet_results[sheet] = sheet_results
            all_content_results.extend(sheet_results)

            print(f"[Cross-Sheet Query] {sheet}: {len(sheet_results)} results")

        # Step 3: If entity identifier provided, re-rank by entity match
        if entity_identifier:
            all_content_results = self._rerank_by_entity(
                all_content_results,
                entity_identifier
            )

        # Step 4: Build enhanced context
        context = self._build_cross_sheet_context(
            structure_results,
            per_sheet_results,
            user_query,
            entity_identifier
        )

        return {
            "query": user_query,
            "entity": entity_identifier,
            "structure_results": structure_results,
            "content_results": all_content_results,
            "per_sheet_results": per_sheet_results,
            "context": context
        }

    def _rerank_by_entity(
        self,
        results: List[Dict[str, Any]],
        entity: str
    ) -> List[Dict[str, Any]]:
        """
        Re-rank results by entity presence

        Args:
            results: Search results
            entity: Entity identifier to boost

        Returns:
            Re-ranked results
        """
        entity_lower = entity.lower()

        # Boost score if entity appears in text
        for result in results:
            if entity_lower in result["text"].lower():
                result["score"] = result["score"] * 1.5  # Boost by 50%
                result["entity_match"] = True
            else:
                result["entity_match"] = False

        # Sort by boosted score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _build_cross_sheet_context(
        self,
        structure_results: List[Dict[str, Any]],
        per_sheet_results: Dict[str, List[Dict[str, Any]]],
        query: str,
        entity: Optional[str] = None
    ) -> str:
        """
        Build enhanced context with clear sheet separation

        Args:
            structure_results: Structure information
            per_sheet_results: Results organized by sheet
            query: Original query
            entity: Optional entity identifier

        Returns:
            Formatted context string
        """
        context_parts = []

        # Header
        context_parts.append("=== CROSS-SHEET QUERY RESULTS ===")
        if entity:
            context_parts.append(f"Entity Focus: {entity}")

        # Structure info
        context_parts.append("\n=== RELEVANT SHEETS ===")
        for i, struct in enumerate(structure_results, 1):
            context_parts.append(f"\n{i}. {struct['sheet']}")
            context_parts.append(f"   Columns: {struct['columns']}")

        # Per-sheet data with clear separation
        context_parts.append("\n\n=== DATA BY SHEET ===")
        for sheet, results in per_sheet_results.items():
            if not results:
                continue

            context_parts.append(f"\n--- {sheet} ---")
            for i, content in enumerate(results, 1):
                text_preview = content["text"][:200]
                entity_marker = " [ENTITY MATCH]" if content.get("entity_match") else ""
                context_parts.append(
                    f"{i}. {text_preview}... (score: {content['score']:.4f}){entity_marker}"
                )

        # Query
        context_parts.append(f"\n\n=== USER QUESTION ===")
        context_parts.append(f"{query}")

        return "\n".join(context_parts)

    def query_with_multi_entity(
        self,
        user_query: str,
        entities: List[str],
        top_k_structure: int = 5,
        top_k_per_sheet: int = 5
    ) -> Dict[str, Any]:
        """
        Query for multiple entities across sheets

        Example: "Compare products A, B, and C"

        Args:
            user_query: User's question
            entities: List of entities to find
            top_k_structure: Number of sheets
            top_k_per_sheet: Results per sheet

        Returns:
            Results organized by entity and sheet
        """
        print(f"\n[Multi-Entity Query] Processing: '{user_query}'")
        print(f"[Multi-Entity Query] Entities: {entities}")

        # Get relevant sheets
        structure_results = self.structure_db.search(user_query, top_k=top_k_structure)
        relevant_sheets = [r["sheet"] for r in structure_results]

        # Search for each entity
        entity_results = {}
        for entity in entities:
            entity_query = f"{user_query} {entity}"
            results = []

            for sheet in relevant_sheets:
                sheet_results = self.content_db.search(
                    entity_query,
                    top_k=top_k_per_sheet,
                    sheet_filter=[sheet]
                )
                results.extend(sheet_results)

            # Filter for entity matches
            entity_results[entity] = [
                r for r in results
                if entity.lower() in r["text"].lower()
            ]

        # Build comparison context
        context = self._build_multi_entity_context(
            structure_results,
            entity_results,
            user_query
        )

        return {
            "query": user_query,
            "entities": entities,
            "structure_results": structure_results,
            "entity_results": entity_results,
            "context": context
        }

    def _build_multi_entity_context(
        self,
        structure_results: List[Dict[str, Any]],
        entity_results: Dict[str, List[Dict[str, Any]]],
        query: str
    ) -> str:
        """Build context for multi-entity comparison"""
        context_parts = []

        context_parts.append("=== MULTI-ENTITY COMPARISON ===")

        # Structure
        context_parts.append("\n=== RELEVANT SHEETS ===")
        for struct in structure_results:
            context_parts.append(f"• {struct['sheet']}: {struct['columns'][:100]}...")

        # Results by entity
        context_parts.append("\n\n=== DATA BY ENTITY ===")
        for entity, results in entity_results.items():
            context_parts.append(f"\n--- {entity} ---")
            if not results:
                context_parts.append("  No data found")
                continue

            # Group by sheet
            by_sheet = {}
            for r in results:
                sheet = r["sheet"]
                if sheet not in by_sheet:
                    by_sheet[sheet] = []
                by_sheet[sheet].append(r)

            for sheet, sheet_results in by_sheet.items():
                context_parts.append(f"  From {sheet}:")
                for sr in sheet_results[:3]:  # Top 3 per sheet
                    context_parts.append(f"    • {sr['text'][:150]}...")

        context_parts.append(f"\n\n=== USER QUESTION ===")
        context_parts.append(f"{query}")

        return "\n".join(context_parts)

    def _empty_result(self, query: str) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "query": query,
            "structure_results": [],
            "content_results": [],
            "context": "No relevant data found for this query."
        }


def demo_cross_sheet_query():
    """
    Demo function showing cross-sheet query capabilities
    """
    print("\n" + "=" * 70)
    print("CROSS-SHEET QUERY DEMO")
    print("=" * 70)

    engine = CrossSheetQueryEngine()
    llm = LLMLayer(model_name="mock")

    # Example 1: Single entity across sheets
    print("\n--- Example 1: Single Entity Query ---")
    query = "What is the serial number and cost for product xyz?"
    results = engine.query_with_joins(
        query,
        entity_identifier="product xyz",
        top_k_structure=5,
        top_k_per_sheet=3
    )

    print("\nPer-sheet breakdown:")
    for sheet, sheet_results in results["per_sheet_results"].items():
        print(f"  {sheet}: {len(sheet_results)} results")

    response = llm.generate_answer(results["context"], query)
    print(f"\nAnswer: {response['answer'][:200]}...")

    # Example 2: Multi-entity comparison
    print("\n\n--- Example 2: Multi-Entity Comparison ---")
    query = "Compare the costs of products A, B, and C"
    results = engine.query_with_multi_entity(
        query,
        entities=["product A", "product B", "product C"],
        top_k_structure=5,
        top_k_per_sheet=3
    )

    print("\nEntity breakdown:")
    for entity, entity_results in results["entity_results"].items():
        print(f"  {entity}: {len(entity_results)} matches")

    response = llm.generate_answer(results["context"], query)
    print(f"\nAnswer: {response['answer'][:200]}...")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo_cross_sheet_query()
