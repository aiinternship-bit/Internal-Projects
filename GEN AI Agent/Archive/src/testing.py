"""
Testing Module
Validates retrieval and LLM outputs at each stage
"""
from typing import Dict, List, Any
from .structure_db import StructureVectorDB
from .content_db import ContentVectorDB
from .query_engine import QueryEngine
from .llm_layer import LLMLayer
from . import config


class ExcelRAGTester:
    """
    Comprehensive testing suite for Excel-RAG system
    """

    def __init__(self, db_path: str = config.DB_PATH):
        """
        Initialize tester

        Args:
            db_path: Path to Milvus database
        """
        self.db_path = db_path
        self.structure_db = StructureVectorDB(db_path)
        self.content_db = ContentVectorDB(db_path)
        self.query_engine = QueryEngine(db_path)
        self.llm = LLMLayer(model_name="mock")  # Use mock by default for testing

    def test_connectivity(self) -> Dict[str, Any]:
        """
        Test 1: Validate DB connections and collection existence

        Returns:
            Test results dictionary
        """
        print("\n=== TEST 1: CONNECTIVITY ===")
        results = {
            "test_name": "Connectivity Test",
            "passed": False,
            "details": {}
        }

        try:
            # Check structure collection
            structure_exists = self.structure_db.client.has_collection(
                config.STRUCTURE_COLLECTION
            )
            results["details"]["structure_collection_exists"] = structure_exists

            # Check content collection
            content_exists = self.content_db.client.has_collection(
                config.CONTENT_COLLECTION
            )
            results["details"]["content_collection_exists"] = content_exists

            # Both must exist
            results["passed"] = structure_exists and content_exists

            if results["passed"]:
                print("✓ Both collections are accessible")
            else:
                print("✗ One or more collections missing")
                if not structure_exists:
                    print(f"  - Missing: {config.STRUCTURE_COLLECTION}")
                if not content_exists:
                    print(f"  - Missing: {config.CONTENT_COLLECTION}")

        except Exception as e:
            results["details"]["error"] = str(e)
            print(f"✗ Connectivity error: {e}")

        return results

    def test_embedding(self, sample_query: str = "digital delivery system") -> Dict[str, Any]:
        """
        Test 2: Encode sample query and verify vector dimensions

        Args:
            sample_query: Query to test

        Returns:
            Test results dictionary
        """
        print(f"\n=== TEST 2: EMBEDDING ===")
        print(f"Query: '{sample_query}'")

        results = {
            "test_name": "Embedding Test",
            "passed": False,
            "details": {"query": sample_query}
        }

        try:
            # Encode using structure DB model (same as content DB)
            query_emb = self.structure_db.model.encode([sample_query])
            emb_dim = query_emb.shape[1]

            results["details"]["embedding_dimension"] = emb_dim
            results["details"]["expected_dimension"] = config.EMBEDDING_DIM

            # Check dimension matches config
            results["passed"] = (emb_dim == config.EMBEDDING_DIM)

            if results["passed"]:
                print(f"✓ Embedding dimension correct: {emb_dim}")
            else:
                print(f"✗ Dimension mismatch: got {emb_dim}, expected {config.EMBEDDING_DIM}")

        except Exception as e:
            results["details"]["error"] = str(e)
            print(f"✗ Embedding error: {e}")

        return results

    def test_retrieval(
        self,
        sample_query: str = "digital delivery system",
        top_k_structure: int = 3,
        top_k_content: int = 5
    ) -> Dict[str, Any]:
        """
        Test 3: Run sample query and validate retrieval results

        Args:
            sample_query: Query to test
            top_k_structure: Number of structure results
            top_k_content: Number of content results

        Returns:
            Test results dictionary
        """
        print(f"\n=== TEST 3: RETRIEVAL ===")
        print(f"Query: '{sample_query}'")

        results = {
            "test_name": "Retrieval Test",
            "passed": False,
            "details": {"query": sample_query}
        }

        try:
            # Test structure retrieval
            print("Testing structure retrieval...")
            structure_results = self.query_engine.search_structure_only(
                sample_query,
                top_k=top_k_structure
            )
            results["details"]["structure_results_count"] = len(structure_results)

            # Test content retrieval
            print("Testing content retrieval...")
            content_results = self.query_engine.search_content_only(
                sample_query,
                top_k=top_k_content
            )
            results["details"]["content_results_count"] = len(content_results)

            # Show top results
            if structure_results:
                print(f"\nTop structure match: {structure_results[0]['sheet']}")
                print(f"  Score: {structure_results[0]['score']:.4f}")
                results["details"]["top_structure_sheet"] = structure_results[0]["sheet"]

            if content_results:
                print(f"\nTop content match: [{content_results[0]['sheet']}]")
                print(f"  Text preview: {content_results[0]['text'][:100]}...")
                print(f"  Score: {content_results[0]['score']:.4f}")
                results["details"]["top_content_sheet"] = content_results[0]["sheet"]

            # Pass if we got results from both
            results["passed"] = len(structure_results) > 0 and len(content_results) > 0

            if results["passed"]:
                print("\n✓ Retrieval successful from both databases")
            else:
                print("\n✗ Retrieval failed to return results")

        except Exception as e:
            results["details"]["error"] = str(e)
            print(f"✗ Retrieval error: {e}")

        return results

    def test_llm(
        self,
        sample_context: str = None,
        sample_query: str = "What is this data about?"
    ) -> Dict[str, Any]:
        """
        Test 4: LLM integration test with sample context

        Args:
            sample_context: Context to provide (if None, generates sample)
            sample_query: Query to answer

        Returns:
            Test results dictionary
        """
        print(f"\n=== TEST 4: LLM INTEGRATION ===")

        results = {
            "test_name": "LLM Integration Test",
            "passed": False,
            "details": {"query": sample_query}
        }

        try:
            # Use provided context or create sample
            if sample_context is None:
                sample_context = """=== RELEVANT EXCEL STRUCTURE ===
1. Sheet: Deliveries, Columns: ['Date', 'Customer', 'Status']

=== RELEVANT DATA ROWS ===
1. [Deliveries] 2024-01-15, ACME Corp, Completed"""

            # Generate answer
            response = self.llm.generate_answer(sample_context, sample_query)

            results["details"]["answer"] = response["answer"]
            results["details"]["model"] = response["model"]
            results["details"]["token_usage"] = response["token_usage"]
            results["details"]["backend"] = response["backend"]

            # Pass if we got an answer
            results["passed"] = len(response["answer"]) > 0

            if results["passed"]:
                print(f"✓ LLM responded successfully")
                print(f"  Model: {response['model']} ({response['backend']})")
                print(f"  Token usage: {response['token_usage']}")
                print(f"  Answer preview: {response['answer'][:200]}...")
            else:
                print("✗ LLM failed to generate answer")

        except Exception as e:
            results["details"]["error"] = str(e)
            print(f"✗ LLM error: {e}")

        return results

    def test_end_to_end(
        self,
        test_query: str = "digital delivery system"
    ) -> Dict[str, Any]:
        """
        Test 5: Full end-to-end pipeline

        Args:
            test_query: Query to test

        Returns:
            Test results dictionary
        """
        print(f"\n=== TEST 5: END-TO-END ===")
        print(f"Query: '{test_query}'")

        results = {
            "test_name": "End-to-End Test",
            "passed": False,
            "details": {"query": test_query}
        }

        try:
            # Execute full query pipeline
            query_results = self.query_engine.query(test_query)

            # Generate LLM answer
            llm_response = self.llm.generate_answer(
                query_results["context"],
                test_query
            )

            # Store results
            results["details"]["structure_count"] = len(query_results["structure_results"])
            results["details"]["content_count"] = len(query_results["content_results"])
            results["details"]["answer"] = llm_response["answer"]
            results["details"]["token_usage"] = llm_response["token_usage"]

            # Pass if we got results and an answer
            results["passed"] = (
                len(query_results["structure_results"]) > 0 and
                len(query_results["content_results"]) > 0 and
                len(llm_response["answer"]) > 0
            )

            if results["passed"]:
                print(f"\n✓ End-to-end pipeline successful")
                print(f"  Retrieved: {results['details']['structure_count']} sheets, "
                      f"{results['details']['content_count']} rows")
                print(f"  Token usage: {results['details']['token_usage']}")
                print(f"\nFinal Answer:\n{llm_response['answer']}")
            else:
                print("\n✗ End-to-end pipeline failed")

        except Exception as e:
            results["details"]["error"] = str(e)
            print(f"✗ End-to-end error: {e}")

        return results

    def run_all_tests(self, sample_query: str = "digital delivery system") -> List[Dict[str, Any]]:
        """
        Run complete test suite

        Args:
            sample_query: Query to use for testing

        Returns:
            List of all test results
        """
        print("\n" + "=" * 60)
        print("EXCEL-RAG SYSTEM TEST SUITE")
        print("=" * 60)

        all_results = []

        # Run tests in sequence
        all_results.append(self.test_connectivity())
        all_results.append(self.test_embedding(sample_query))
        all_results.append(self.test_retrieval(sample_query))
        all_results.append(self.test_llm())
        all_results.append(self.test_end_to_end(sample_query))

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in all_results if r["passed"])
        total = len(all_results)

        for result in all_results:
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"{status}: {result['test_name']}")

        print(f"\nTotal: {passed}/{total} tests passed")

        return all_results
