"""
Query Engine Module
Implements dual-vector retrieval strategy for Excel-RAG
"""
from typing import Dict, Any, List
from .structure_db import StructureVectorDB
from .content_db import ContentVectorDB
from . import config


class QueryEngine:
    """
    Handles dual-stage vector retrieval: structure → content
    """

    def __init__(self, db_path: str = config.DB_PATH):
        """
        Initialize query engine with both structure and content DBs

        Args:
            db_path: Path to Milvus Lite database file
        """
        self.structure_db = StructureVectorDB(db_path)
        self.content_db = ContentVectorDB(db_path)

    def query(
        self,
        user_query: str,
        top_k_structure: int = config.TOP_K_STRUCTURE,
        top_k_content: int = config.TOP_K_CONTENT
    ) -> Dict[str, Any]:
        """
        Execute dual-vector retrieval on user query

        Args:
            user_query: User's natural language query
            top_k_structure: Number of sheets/columns to retrieve
            top_k_content: Number of content rows to retrieve

        Returns:
            Dictionary containing:
                - query: Original query
                - structure_results: Retrieved sheet/column info
                - content_results: Retrieved row content
                - context: Formatted context for LLM
        """
        print(f"\nProcessing query: '{user_query}'")

        # Step 1: Structure Retrieval
        print(f"Step 1: Searching structure DB for top-{top_k_structure} sheets/columns...")
        structure_results = self.structure_db.search(user_query, top_k=top_k_structure)

        if not structure_results:
            print("No structure results found")
            return {
                "query": user_query,
                "structure_results": [],
                "content_results": [],
                "context": "No relevant data found for this query."
            }

        # Extract sheet names for filtering content search
        relevant_sheets = [r["sheet"] for r in structure_results]
        print(f"Found relevant sheets: {relevant_sheets}")

        # Step 2: Content Retrieval (filtered by sheets)
        print(f"Step 2: Searching content DB for top-{top_k_content} rows in relevant sheets...")
        content_results = self.content_db.search(
            user_query,
            top_k=top_k_content,
            sheet_filter=relevant_sheets
        )

        print(f"Retrieved {len(content_results)} content rows")

        # Step 3: Build context for LLM
        context = self._build_context(structure_results, content_results, user_query)

        return {
            "query": user_query,
            "structure_results": structure_results,
            "content_results": content_results,
            "context": context
        }

    def _build_context(
        self,
        structure_results: List[Dict[str, Any]],
        content_results: List[Dict[str, Any]],
        query: str
    ) -> str:
        """
        Build formatted context string for LLM

        Args:
            structure_results: Retrieved structure information
            content_results: Retrieved content rows
            query: Original user query

        Returns:
            Formatted context string
        """
        context_parts = []

        # Add structure information
        context_parts.append("=== RELEVANT EXCEL STRUCTURE ===")
        for i, struct in enumerate(structure_results, 1):
            context_parts.append(f"\n{i}. Sheet: {struct['sheet']}")
            context_parts.append(f"   Columns: {struct['columns']}")
            context_parts.append(f"   Relevance: {struct['score']:.4f}")

        # Add content information
        context_parts.append("\n\n=== RELEVANT DATA ROWS ===")
        for i, content in enumerate(content_results, 1):
            context_parts.append(f"\n{i}. [{content['sheet']}] {content['text'][:200]}...")
            context_parts.append(f"   Relevance: {content['score']:.4f}")

        # Add query at the end
        context_parts.append(f"\n\n=== USER QUESTION ===")
        context_parts.append(f"{query}")

        return "\n".join(context_parts)

    def search_structure_only(self, query: str, top_k: int = config.TOP_K_STRUCTURE) -> List[Dict[str, Any]]:
        """
        Search only the structure database (useful for schema exploration)

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of structure results
        """
        return self.structure_db.search(query, top_k=top_k)

    def search_content_only(
        self,
        query: str,
        top_k: int = config.TOP_K_CONTENT,
        sheet_filter: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search only the content database (useful for direct content lookup)

        Args:
            query: Search query
            top_k: Number of results
            sheet_filter: Optional sheet filter

        Returns:
            List of content results
        """
        return self.content_db.search(query, top_k=top_k, sheet_filter=sheet_filter)

    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector databases

        Returns:
            Dictionary with database statistics
        """
        stats = {
            "structure_collection": config.STRUCTURE_COLLECTION,
            "content_collection": config.CONTENT_COLLECTION,
            "db_path": self.structure_db.db_path
        }

        try:
            # Check if collections exist
            stats["structure_exists"] = self.structure_db.client.has_collection(
                config.STRUCTURE_COLLECTION
            )
            stats["content_exists"] = self.content_db.client.has_collection(
                config.CONTENT_COLLECTION
            )
        except Exception as e:
            stats["error"] = str(e)

        return stats
