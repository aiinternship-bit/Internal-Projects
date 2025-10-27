"""
shared/tools/code_search.py

Semantic code search utilities for finding patterns, best practices, and solutions.
Provides higher-level search abstractions on top of Vector DB.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class CodePattern:
    """Represents a code pattern extracted from search results."""
    pattern_type: str  # "function", "class", "pattern", "idiom"
    language: str
    code: str
    description: str
    use_cases: List[str]
    quality_score: float
    complexity_score: float
    metadata: Dict[str, Any]


@dataclass
class BestPractice:
    """Represents a best practice example."""
    title: str
    description: str
    example_code: str
    language: str
    category: str  # "security", "performance", "maintainability", etc.
    rationale: str
    anti_patterns: List[str]  # What to avoid
    references: List[str]


class CodeSearchEngine:
    """
    Advanced code search engine providing semantic search capabilities.
    """

    def __init__(self, vector_db_client):
        """
        Initialize code search engine.

        Args:
            vector_db_client: UniversalVectorDBClient instance
        """
        self.vector_db = vector_db_client

    # ============================================================================
    # Semantic Search Methods
    # ============================================================================

    def semantic_search(
        self,
        query: str,
        language: Optional[str] = None,
        component_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search for code or documentation.

        Args:
            query: Natural language or code query
            language: Optional programming language filter
            component_type: Optional component type filter
            top_k: Number of results to return

        Returns:
            List of search results with similarity scores
        """
        filters = {}
        if language:
            filters["language"] = language
        if component_type:
            filters["component_type"] = component_type

        results = self.vector_db.search_similar_implementations(
            query=query,
            filters=filters,
            top_k=top_k
        )

        return [
            {
                "content": r.content,
                "metadata": r.metadata,
                "similarity_score": r.similarity_score,
                "language": r.metadata.get("language", "unknown"),
                "file_path": r.metadata.get("file_path", "")
            }
            for r in results
        ]

    def search_by_function_signature(
        self,
        function_name: str,
        parameters: Optional[List[str]] = None,
        return_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for functions with similar signatures.

        Args:
            function_name: Name of the function
            parameters: Optional parameter names/types
            return_type: Optional return type
            language: Programming language

        Returns:
            List of matching functions
        """
        # Build query
        query_parts = [f"function {function_name}"]
        if parameters:
            query_parts.append(f"with parameters {', '.join(parameters)}")
        if return_type:
            query_parts.append(f"returns {return_type}")

        query = " ".join(query_parts)

        filters = {"type": "function"}
        if language:
            filters["language"] = language

        results = self.vector_db.search_similar_implementations(
            query=query,
            filters=filters,
            top_k=10
        )

        return [
            {
                "function_name": r.metadata.get("function_name", function_name),
                "signature": r.metadata.get("signature", ""),
                "code": r.content,
                "language": r.metadata.get("language", "unknown"),
                "complexity": r.metadata.get("complexity_score", 0)
            }
            for r in results
        ]

    def search_by_pattern(
        self,
        pattern_name: str,
        language: Optional[str] = None
    ) -> List[CodePattern]:
        """
        Search for specific code patterns (e.g., "singleton", "factory").

        Args:
            pattern_name: Name of the pattern
            language: Optional language filter

        Returns:
            List of CodePattern objects
        """
        results = self.vector_db.retrieve_architectural_patterns(
            pattern_name=pattern_name
        )

        patterns = []
        for r in results:
            if language and r.metadata.get("language") != language:
                continue

            pattern = CodePattern(
                pattern_type=pattern_name,
                language=r.metadata.get("language", "unknown"),
                code=r.content,
                description=r.metadata.get("description", ""),
                use_cases=r.metadata.get("use_cases", []),
                quality_score=r.metadata.get("quality_score", 0.0),
                complexity_score=r.metadata.get("complexity_score", 0.0),
                metadata=r.metadata
            )
            patterns.append(pattern)

        return patterns

    # ============================================================================
    # Pattern Matching Methods
    # ============================================================================

    def pattern_match(
        self,
        code_snippet: str,
        pattern_type: str,
        language: str
    ) -> Tuple[bool, float, str]:
        """
        Check if code snippet matches a specific pattern.

        Args:
            code_snippet: Code to analyze
            pattern_type: Type of pattern to check
            language: Programming language

        Returns:
            Tuple of (matches, confidence, explanation)
        """
        # Get pattern examples
        patterns = self.search_by_pattern(pattern_type, language)

        if not patterns:
            return (False, 0.0, f"No examples found for pattern '{pattern_type}'")

        # Simple heuristic: check for key structural elements
        # In production, this would use more sophisticated AST analysis
        best_match_score = 0.0
        explanation = ""

        for pattern in patterns:
            score = self._calculate_pattern_similarity(code_snippet, pattern.code)
            if score > best_match_score:
                best_match_score = score
                explanation = f"Code structure matches {pattern_type} pattern ({score:.2%} similarity)"

        matches = best_match_score > 0.7
        return (matches, best_match_score, explanation)

    def extract_patterns_from_code(
        self,
        code: str,
        language: str
    ) -> List[str]:
        """
        Extract recognized patterns from code.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            List of pattern names found in the code
        """
        # Common patterns to check for
        pattern_signatures = {
            "singleton": ["static.*instance", "private.*constructor"],
            "factory": ["create.*", "make.*", "build.*"],
            "observer": ["subscribe", "notify", "listener"],
            "repository": ["find.*", "save", "delete", "get.*ById"],
            "decorator": ["wrapper", "decorated"],
            "strategy": ["algorithm", "strategy", "execute"],
            "adapter": ["adapt", "wrapper", "interface"]
        }

        found_patterns = []
        code_lower = code.lower()

        for pattern_name, signatures in pattern_signatures.items():
            for signature in signatures:
                if re.search(signature, code_lower):
                    found_patterns.append(pattern_name)
                    break

        return list(set(found_patterns))  # Remove duplicates

    # ============================================================================
    # Similarity and Comparison Methods
    # ============================================================================

    def similarity_score(
        self,
        code_a: str,
        code_b: str,
        method: str = "structural"
    ) -> float:
        """
        Calculate similarity between two code snippets.

        Args:
            code_a: First code snippet
            code_b: Second code snippet
            method: Similarity method ("structural", "semantic", "lexical")

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if method == "structural":
            return self._structural_similarity(code_a, code_b)
        elif method == "semantic":
            return self._semantic_similarity(code_a, code_b)
        elif method == "lexical":
            return self._lexical_similarity(code_a, code_b)
        else:
            raise ValueError(f"Unknown similarity method: {method}")

    def _structural_similarity(self, code_a: str, code_b: str) -> float:
        """Calculate structural similarity based on code structure."""
        # Simple heuristic: compare line counts, brace counts, indentation patterns
        lines_a = code_a.split('\n')
        lines_b = code_b.split('\n')

        # Line count similarity
        line_diff = abs(len(lines_a) - len(lines_b))
        max_lines = max(len(lines_a), len(lines_b))
        line_similarity = 1.0 - (line_diff / max_lines) if max_lines > 0 else 0.0

        # Brace/bracket similarity
        braces_a = code_a.count('{') + code_a.count('(') + code_a.count('[')
        braces_b = code_b.count('{') + code_b.count('(') + code_b.count('[')
        brace_diff = abs(braces_a - braces_b)
        max_braces = max(braces_a, braces_b)
        brace_similarity = 1.0 - (brace_diff / max_braces) if max_braces > 0 else 0.0

        # Combined score
        return (line_similarity * 0.6 + brace_similarity * 0.4)

    def _semantic_similarity(self, code_a: str, code_b: str) -> float:
        """Calculate semantic similarity (would use embeddings in production)."""
        # Placeholder: In production, this would use embeddings from Vector DB
        # For now, use lexical similarity as approximation
        return self._lexical_similarity(code_a, code_b)

    def _lexical_similarity(self, code_a: str, code_b: str) -> float:
        """Calculate lexical similarity using Jaccard index."""
        # Tokenize code (simple word-based tokenization)
        tokens_a = set(re.findall(r'\w+', code_a.lower()))
        tokens_b = set(re.findall(r'\w+', code_b.lower()))

        # Jaccard similarity
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)

        return intersection / union if union > 0 else 0.0

    def _calculate_pattern_similarity(self, code: str, pattern_code: str) -> float:
        """Calculate how well code matches a pattern."""
        # Use combination of structural and lexical similarity
        structural = self._structural_similarity(code, pattern_code)
        lexical = self._lexical_similarity(code, pattern_code)

        return (structural * 0.7 + lexical * 0.3)

    # ============================================================================
    # Best Practices Extraction
    # ============================================================================

    def extract_best_practices_from_results(
        self,
        results: List[Any],
        language: str,
        category: Optional[str] = None
    ) -> List[BestPractice]:
        """
        Extract best practices from search results.

        Args:
            results: Query results from Vector DB
            language: Programming language
            category: Optional category filter

        Returns:
            List of BestPractice objects
        """
        best_practices = []

        for result in results:
            metadata = result.metadata if hasattr(result, 'metadata') else result.get('metadata', {})

            # Only include high-quality results
            quality_score = metadata.get("quality_score", 0.0)
            if quality_score < 0.7:
                continue

            # Filter by category if specified
            result_category = metadata.get("category", "general")
            if category and result_category != category:
                continue

            practice = BestPractice(
                title=metadata.get("title", "Best Practice"),
                description=metadata.get("description", ""),
                example_code=result.content if hasattr(result, 'content') else result.get('content', ''),
                language=language,
                category=result_category,
                rationale=metadata.get("rationale", ""),
                anti_patterns=metadata.get("anti_patterns", []),
                references=metadata.get("references", [])
            )
            best_practices.append(practice)

        return best_practices

    def get_best_practices_for_component(
        self,
        component_type: str,
        language: str,
        categories: Optional[List[str]] = None
    ) -> List[BestPractice]:
        """
        Get best practices for a specific component type.

        Args:
            component_type: Type of component
            language: Programming language
            categories: Optional list of categories to include

        Returns:
            List of relevant best practices
        """
        results = self.vector_db.get_best_practices(
            component_type=component_type,
            language=language
        )

        if categories:
            all_practices = []
            for category in categories:
                practices = self.extract_best_practices_from_results(
                    results, language, category
                )
                all_practices.extend(practices)
            return all_practices
        else:
            return self.extract_best_practices_from_results(results, language)

    # ============================================================================
    # Advanced Search Methods
    # ============================================================================

    def search_by_complexity(
        self,
        max_complexity: int,
        language: str,
        component_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for code examples with specific complexity constraints.

        Args:
            max_complexity: Maximum cyclomatic complexity
            language: Programming language
            component_type: Optional component type

        Returns:
            List of code examples within complexity bounds
        """
        filters = {
            "language": language,
            "complexity_score": {"$lte": max_complexity}
        }

        if component_type:
            filters["component_type"] = component_type

        query = f"simple {component_type or 'code'} examples in {language}"

        results = self.vector_db.search_similar_implementations(
            query=query,
            filters=filters,
            top_k=10
        )

        return [
            {
                "code": r.content,
                "complexity": r.metadata.get("complexity_score", 0),
                "language": language,
                "component_type": r.metadata.get("component_type", "")
            }
            for r in results
        ]

    def search_by_nfr(
        self,
        nfr_type: str,
        threshold: float,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Search for implementations meeting specific NFR requirements.

        Args:
            nfr_type: Type of NFR ("latency", "throughput", "memory")
            threshold: Threshold value
            language: Programming language

        Returns:
            List of implementations meeting NFR
        """
        query = f"high performance {nfr_type} optimized code in {language}"

        filters = {
            "language": language,
            f"nfr_{nfr_type}": {"$lte": threshold}
        }

        results = self.vector_db.search_similar_implementations(
            query=query,
            filters=filters,
            top_k=5
        )

        return [
            {
                "code": r.content,
                "nfr_type": nfr_type,
                "nfr_value": r.metadata.get(f"nfr_{nfr_type}", 0),
                "language": language
            }
            for r in results
        ]

    def find_refactoring_examples(
        self,
        anti_pattern: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Find examples of refactoring from anti-patterns to best practices.

        Args:
            anti_pattern: Name of the anti-pattern
            language: Programming language

        Returns:
            List of before/after refactoring examples
        """
        query = f"refactor {anti_pattern} anti-pattern in {language}"

        filters = {
            "language": language,
            "is_refactoring_example": True,
            "anti_pattern": anti_pattern
        }

        results = self.vector_db.search_similar_implementations(
            query=query,
            filters=filters,
            top_k=5
        )

        return [
            {
                "before": r.metadata.get("before_code", ""),
                "after": r.content,
                "explanation": r.metadata.get("explanation", ""),
                "anti_pattern": anti_pattern,
                "language": language
            }
            for r in results
        ]
