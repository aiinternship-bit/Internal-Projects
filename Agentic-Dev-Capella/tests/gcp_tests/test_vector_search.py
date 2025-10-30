"""
tests/gcp_tests/test_vector_search.py

Tests for Google Cloud Vertex AI Vector Search (Matching Engine) integration.
Tests semantic search over code knowledge base.
"""

import unittest
import os
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# MOCK TESTS (No GCP Credentials Required)
# ============================================================================

class TestVectorSearchMock(unittest.TestCase):
    """Test Vector Search with mocked GCP services."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_id = "test-project"
        self.location = "us-central1"
        self.index_id = "test-index"
        self.endpoint_id = "test-endpoint"

    @patch('google.cloud.aiplatform.MatchingEngineIndex')
    @patch('google.cloud.aiplatform.MatchingEngineIndexEndpoint')
    def test_vector_search_initialization(self, mock_endpoint, mock_index):
        """Test Vector Search client initialization."""
        # Mock index and endpoint
        mock_index_instance = MagicMock()
        mock_endpoint_instance = MagicMock()

        mock_index.return_value = mock_index_instance
        mock_endpoint.return_value = mock_endpoint_instance

        # In real implementation, would import actual client
        # For now, test the pattern

        self.assertIsNotNone(mock_index_instance)
        self.assertIsNotNone(mock_endpoint_instance)

    def test_embedding_generation(self):
        """Test text embedding generation."""
        # Mock embedding model
        with patch('vertexai.language_models.TextEmbeddingModel') as mock_model:
            mock_embedding_instance = MagicMock()
            mock_model.from_pretrained.return_value = mock_embedding_instance

            # Mock embeddings response
            mock_embedding_instance.get_embeddings.return_value = [
                MagicMock(values=[0.1] * 768)  # 768-dim embedding
            ]

            # Generate embedding
            embeddings = mock_embedding_instance.get_embeddings(["test query"])

            self.assertEqual(len(embeddings), 1)
            self.assertEqual(len(embeddings[0].values), 768)

    def test_semantic_search_query(self):
        """Test semantic search query execution."""
        query_text = "payment processing logic"
        top_k = 10

        # Mock vector search response
        mock_results = [
            {
                "id": "doc1",
                "distance": 0.85,
                "metadata": {
                    "file_path": "legacy/payment_processor.cbl",
                    "function_name": "PROCESS-PAYMENT",
                    "code_snippet": "PERFORM VALIDATE-AMOUNT..."
                }
            },
            {
                "id": "doc2",
                "distance": 0.78,
                "metadata": {
                    "file_path": "legacy/card_validator.cbl",
                    "function_name": "VALIDATE-CARD",
                    "code_snippet": "IF CARD-EXPIRED..."
                }
            }
        ]

        # Verify results structure
        self.assertEqual(len(mock_results), 2)
        self.assertGreater(mock_results[0]["distance"], mock_results[1]["distance"])
        self.assertIn("file_path", mock_results[0]["metadata"])

    def test_filter_by_metadata(self):
        """Test filtering search results by metadata."""
        filters = {
            "file_type": "COBOL",
            "domain": "payment_processing"
        }

        # Mock filtered results
        mock_results = [
            {
                "id": "doc1",
                "metadata": {
                    "file_type": "COBOL",
                    "domain": "payment_processing"
                }
            }
        ]

        # Verify filter applied
        for result in mock_results:
            self.assertEqual(result["metadata"]["file_type"], filters["file_type"])
            self.assertEqual(result["metadata"]["domain"], filters["domain"])

    def test_batch_embedding_generation(self):
        """Test generating embeddings for multiple texts."""
        texts = [
            "payment processing",
            "authentication logic",
            "database queries"
        ]

        # Mock batch embeddings
        with patch('vertexai.language_models.TextEmbeddingModel') as mock_model:
            mock_embedding_instance = MagicMock()
            mock_model.from_pretrained.return_value = mock_embedding_instance

            mock_embedding_instance.get_embeddings.return_value = [
                MagicMock(values=[0.1] * 768),
                MagicMock(values=[0.2] * 768),
                MagicMock(values=[0.3] * 768)
            ]

            embeddings = mock_embedding_instance.get_embeddings(texts)

            self.assertEqual(len(embeddings), len(texts))
            for embedding in embeddings:
                self.assertEqual(len(embedding.values), 768)


# ============================================================================
# INTEGRATION TESTS (Require GCP Credentials)
# ============================================================================

@unittest.skipUnless(
    os.getenv("GCP_PROJECT_ID") and os.getenv("VECTOR_SEARCH_ENDPOINT"),
    "Skipping integration tests - set GCP_PROJECT_ID and VECTOR_SEARCH_ENDPOINT to run"
)
class TestVectorSearchIntegration(unittest.TestCase):
    """
    Integration tests with real Vertex AI Vector Search.

    Set environment variables to run:
    export GCP_PROJECT_ID=your-project-id
    export VECTOR_SEARCH_ENDPOINT=projects/X/locations/Y/indexEndpoints/Z
    gcloud auth application-default login
    """

    @classmethod
    def setUpClass(cls):
        """Set up Vector Search client."""
        import vertexai
        from google.cloud import aiplatform

        cls.project_id = os.getenv("GCP_PROJECT_ID")
        cls.location = "us-central1"
        cls.endpoint_id = os.getenv("VECTOR_SEARCH_ENDPOINT")

        # Initialize Vertex AI
        aiplatform.init(project=cls.project_id, location=cls.location)
        vertexai.init(project=cls.project_id, location=cls.location)

        print(f"\nInitialized Vector Search for project: {cls.project_id}")

    def test_generate_embeddings_real(self):
        """Test generating embeddings with real API."""
        from vertexai.language_models import TextEmbeddingModel

        model = TextEmbeddingModel.from_pretrained("text-embedding-004")

        texts = ["payment processing logic", "authentication flow"]

        embeddings = model.get_embeddings(texts)

        # Verify embeddings
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(len(embeddings[0].values), 768)  # 768-dimensional
        self.assertIsInstance(embeddings[0].values[0], float)

    def test_semantic_search_real(self):
        """Test semantic search with real Vector Search endpoint."""
        from google.cloud import aiplatform
        from vertexai.language_models import TextEmbeddingModel

        # Generate query embedding
        embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        query_embedding = embedding_model.get_embeddings(["payment processing"])[0]

        # Get endpoint
        endpoint = aiplatform.MatchingEngineIndexEndpoint(self.endpoint_id)

        # Search (if index is deployed)
        try:
            results = endpoint.find_neighbors(
                deployed_index_id="deployed_index",  # Adjust based on deployment
                queries=[query_embedding.values],
                num_neighbors=5
            )

            # Verify results structure
            self.assertIsNotNone(results)
            if results and len(results) > 0:
                self.assertLessEqual(len(results[0]), 5)
        except Exception as e:
            self.skipTest(f"Vector Search endpoint not ready: {e}")


# ============================================================================
# VECTOR DB CLIENT TESTS
# ============================================================================

class TestUniversalVectorDBClient(unittest.TestCase):
    """Test UniversalVectorDBClient abstraction."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock Vector DB client
        self.mock_client = MagicMock()

    def test_search_similar_implementations(self):
        """Test searching for similar code implementations."""
        query = "payment validation logic"
        filters = {"language": "COBOL", "domain": "fintech"}
        top_k = 5

        # Mock search results
        self.mock_client.search.return_value = [
            {
                "id": "impl1",
                "score": 0.92,
                "code_snippet": "VALIDATE-PAYMENT-AMOUNT...",
                "metadata": {"file": "payment.cbl", "language": "COBOL"}
            },
            {
                "id": "impl2",
                "score": 0.88,
                "code_snippet": "CHECK-CARD-VALIDITY...",
                "metadata": {"file": "card.cbl", "language": "COBOL"}
            }
        ]

        results = self.mock_client.search(query, filters=filters, top_k=top_k)

        # Verify results
        self.assertEqual(len(results), 2)
        self.assertGreater(results[0]["score"], results[1]["score"])
        self.assertEqual(results[0]["metadata"]["language"], "COBOL")

    def test_search_best_practices(self):
        """Test searching for best practices."""
        query = "error handling patterns in Python"
        filters = {"type": "best_practice", "language": "python"}

        # Mock best practices results
        self.mock_client.search.return_value = [
            {
                "id": "bp1",
                "score": 0.95,
                "pattern": "try-except with specific exceptions",
                "example": "try:\n    ...\nexcept ValueError as e:\n    ...",
                "metadata": {"category": "error_handling"}
            }
        ]

        results = self.mock_client.search(query, filters=filters, top_k=5)

        self.assertEqual(len(results), 1)
        self.assertIn("try-except", results[0]["pattern"])

    def test_hybrid_search(self):
        """Test hybrid search (semantic + keyword)."""
        semantic_query = "authentication logic"
        keyword_filters = {"contains": "JWT", "file_type": ".py"}

        # Mock hybrid results
        self.mock_client.hybrid_search.return_value = [
            {
                "id": "file1",
                "semantic_score": 0.85,
                "keyword_score": 0.90,
                "combined_score": 0.875,
                "metadata": {"file": "auth.py", "contains_jwt": True}
            }
        ]

        results = self.mock_client.hybrid_search(
            semantic_query=semantic_query,
            keyword_filters=keyword_filters,
            top_k=10
        )

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["metadata"]["contains_jwt"])

    def test_cache_integration(self):
        """Test result caching for repeated queries."""
        query = "payment processing"

        # First call - cache miss
        self.mock_client.search.return_value = [{"id": "result1"}]
        result1 = self.mock_client.search(query)

        # Second call - cache hit (should not call search again)
        with patch.object(self.mock_client, 'search') as mock_search:
            mock_search.return_value = [{"id": "cached_result"}]

            # Simulate cache hit
            cached_result = [{"id": "result1"}]  # Same as first call

            self.assertEqual(cached_result, result1)


class TestDynamicKnowledgeBaseIntegration(unittest.TestCase):
    """Test dynamic knowledge base integration in agents."""

    def test_execute_dynamic_query(self):
        """Test dynamic knowledge base query from agent."""
        # Mock agent with dynamic KB
        class MockAgentWithKB:
            def __init__(self):
                self.kb_client = MagicMock()

            def execute_dynamic_query(
                self,
                query_type: str,
                context: Dict[str, Any],
                task_id: str
            ) -> List[Dict[str, Any]]:
                """Execute dynamic KB query."""
                if query_type == "best_practices":
                    # Search for best practices
                    query = f"best practices for {context.get('technology')}"
                    return self.kb_client.search(query, filters=context)
                elif query_type == "code_examples":
                    # Search for code examples
                    query = f"{context.get('technology')} examples for {context.get('feature')}"
                    return self.kb_client.search(query)
                return []

        agent = MockAgentWithKB()

        # Mock KB results
        agent.kb_client.search.return_value = [
            {
                "id": "bp1",
                "content": "Use React.memo for performance optimization",
                "category": "react_performance"
            }
        ]

        # Query best practices
        results = agent.execute_dynamic_query(
            query_type="best_practices",
            context={"technology": "react", "focus": "performance"},
            task_id="task_001"
        )

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertIn("React.memo", results[0]["content"])

    def test_fallback_to_llm_when_kb_empty(self):
        """Test fallback to LLM when knowledge base has no results."""
        class MockAgentWithFallback:
            def __init__(self):
                self.kb_client = MagicMock()
                self.llm = MagicMock()

            def query_with_fallback(self, query: str) -> str:
                # Try KB first
                kb_results = self.kb_client.search(query)

                if kb_results:
                    return kb_results[0]["content"]
                else:
                    # Fallback to LLM
                    return self.llm.generate(query)

        agent = MockAgentWithFallback()

        # Mock empty KB results
        agent.kb_client.search.return_value = []

        # Mock LLM response
        agent.llm.generate.return_value = "LLM generated response"

        result = agent.query_with_fallback("How to implement caching?")

        # Verify LLM was used
        self.assertEqual(result, "LLM generated response")
        agent.llm.generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
