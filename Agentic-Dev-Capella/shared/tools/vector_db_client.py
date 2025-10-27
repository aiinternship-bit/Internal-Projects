"""
shared/tools/vector_db_client.py

Enhanced Universal Vector DB Client with dynamic, periodic query capabilities.
Provides intelligent knowledge base access for all coding agents.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
import hashlib
import json

from .vector_db import VectorDBInterface, create_vector_db_interface


@dataclass
class QueryResult:
    """Structured result from a Vector DB query."""
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    query_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QueryContext:
    """Context for a knowledge base query."""
    stage: str  # "initialization", "checkpoint", "error", "validation_fail", "pre_validation"
    task_id: str
    component_type: Optional[str] = None
    language: Optional[str] = None
    current_progress: float = 0.0  # 0.0 to 1.0
    error_info: Optional[Dict[str, Any]] = None
    validation_feedback: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


class QueryCache:
    """Simple in-memory cache for Vector DB query results."""

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize query cache.

        Args:
            ttl_seconds: Time-to-live for cached results (default: 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def _generate_key(self, query: str, filters: Optional[Dict] = None) -> str:
        """Generate cache key from query and filters."""
        key_data = {"query": query, "filters": filters or {}}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, query: str, filters: Optional[Dict] = None) -> Optional[List[QueryResult]]:
        """Retrieve cached results if available and not expired."""
        key = self._generate_key(query, filters)

        if key in self._cache:
            cached_data = self._cache[key]
            age = datetime.utcnow() - cached_data["timestamp"]

            if age < self._ttl:
                return cached_data["results"]
            else:
                # Expired, remove from cache
                del self._cache[key]

        return None

    def set(self, query: str, filters: Optional[Dict], results: List[QueryResult]):
        """Store results in cache."""
        key = self._generate_key(query, filters)
        self._cache[key] = {
            "results": results,
            "timestamp": datetime.utcnow()
        }

    def clear(self):
        """Clear all cached results."""
        self._cache.clear()

    def size(self) -> int:
        """Return number of cached queries."""
        return len(self._cache)


class UniversalVectorDBClient:
    """
    Enhanced Vector DB client with dynamic, periodic query capabilities.
    Provides intelligent knowledge base access for all coding agents.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        enable_cache: bool = True,
        cache_ttl_seconds: int = 300,
        max_queries_per_task: int = 50,
        query_timeout_seconds: int = 5
    ):
        """
        Initialize Universal Vector DB Client.

        Args:
            config: Vector DB configuration
            enable_cache: Enable query result caching
            cache_ttl_seconds: Cache time-to-live in seconds
            max_queries_per_task: Maximum queries allowed per task
            query_timeout_seconds: Timeout for individual queries
        """
        self._vector_db = create_vector_db_interface()
        self._cache = QueryCache(ttl_seconds=cache_ttl_seconds) if enable_cache else None
        self._max_queries_per_task = max_queries_per_task
        self._query_timeout = query_timeout_seconds

        # Query tracking
        self._query_counts: Dict[str, int] = {}  # task_id -> count
        self._query_history: List[Dict[str, Any]] = []
        self._total_queries = 0
        self._cache_hits = 0
        self._cache_misses = 0

    # ============================================================================
    # Core Query Methods
    # ============================================================================

    def search_similar_implementations(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Search for similar code implementations in the knowledge base.

        Args:
            query: Natural language or code query
            filters: Optional filters (language, component_type, etc.)
            top_k: Number of results to return
            task_id: Task identifier for tracking

        Returns:
            List of similar implementations with similarity scores
        """
        # Check cache first
        if self._cache:
            cached = self._cache.get(query, filters)
            if cached:
                self._cache_hits += 1
                return cached
            self._cache_misses += 1

        # Execute query
        results = self._execute_query(
            query=query,
            query_type="similar_implementations",
            filters=filters,
            top_k=top_k,
            task_id=task_id
        )

        # Cache results
        if self._cache:
            self._cache.set(query, filters, results)

        return results

    def get_best_practices(
        self,
        component_type: str,
        language: str,
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Retrieve best practices for a specific component type and language.

        Args:
            component_type: Type of component (e.g., "api", "service", "controller")
            language: Programming language
            task_id: Task identifier for tracking

        Returns:
            List of best practice examples
        """
        query = f"best practices for {component_type} in {language}"
        filters = {
            "component_type": component_type,
            "language": language,
            "is_best_practice": True
        }

        return self.search_similar_implementations(
            query=query,
            filters=filters,
            top_k=3,
            task_id=task_id
        )

    def retrieve_architectural_patterns(
        self,
        pattern_name: str,
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Retrieve implementations of a specific architectural pattern.

        Args:
            pattern_name: Name of the pattern (e.g., "repository", "factory", "observer")
            task_id: Task identifier for tracking

        Returns:
            List of pattern implementations
        """
        query = f"architectural pattern {pattern_name} implementation"
        filters = {
            "pattern_type": pattern_name,
            "is_pattern_example": True
        }

        return self._execute_query(
            query=query,
            query_type="architectural_pattern",
            filters=filters,
            top_k=3,
            task_id=task_id
        )

    def find_related_components(
        self,
        component_id: str,
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Find components related to a specific component.

        Args:
            component_id: Component identifier
            task_id: Task identifier for tracking

        Returns:
            List of related components
        """
        # Get dependency graph
        dep_graph = self._vector_db.get_dependency_graph(component_id, depth=2)

        # Convert to QueryResult format
        results = []
        for dep in dep_graph.get("dependencies", []):
            results.append(QueryResult(
                content=f"Component {dep['id']} ({dep['type']})",
                metadata={
                    "component_id": dep["id"],
                    "relationship": dep["relationship"],
                    "type": dep["type"]
                },
                similarity_score=1.0,
                query_type="related_components"
            ))

        self._track_query("related_components", task_id)
        return results

    # ============================================================================
    # Contextual Query Methods (Dynamic KB Integration)
    # ============================================================================

    def query_at_checkpoint(
        self,
        context: QueryContext,
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Smart query at periodic checkpoints based on context.

        Args:
            context: Current execution context
            task_id: Task identifier for tracking

        Returns:
            Contextually relevant results
        """
        stage = context.stage

        if stage == "initialization":
            return self._query_initialization(context, task_id)
        elif stage == "checkpoint":
            return self._query_checkpoint(context, task_id)
        elif stage == "error":
            return self._query_error(context, task_id)
        elif stage == "validation_fail":
            return self._query_validation_fail(context, task_id)
        elif stage == "pre_validation":
            return self._query_pre_validation(context, task_id)
        else:
            # Default: general guidance
            return self._query_general(context, task_id)

    def find_error_solutions(
        self,
        error_type: str,
        context: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Find solutions to similar errors from the knowledge base.

        Args:
            error_type: Type of error encountered
            context: Error context (message, stack trace, etc.)
            task_id: Task identifier for tracking

        Returns:
            List of solutions to similar errors
        """
        error_msg = context.get("error_message", "")
        query = f"solution for {error_type} error: {error_msg[:100]}"

        filters = {
            "error_type": error_type,
            "has_solution": True
        }

        return self._execute_query(
            query=query,
            query_type="error_solution",
            filters=filters,
            top_k=5,
            task_id=task_id
        )

    def validate_against_patterns(
        self,
        code_snippet: str,
        component_type: str,
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Validate code snippet against established patterns in the knowledge base.

        Args:
            code_snippet: Code to validate
            component_type: Type of component
            task_id: Task identifier for tracking

        Returns:
            List of similar patterns for comparison
        """
        query = f"validate {component_type} implementation"
        filters = {
            "component_type": component_type,
            "is_validated": True,
            "quality_score": {"$gte": 0.8}
        }

        return self._execute_query(
            query=query,
            query_type="pattern_validation",
            filters=filters,
            top_k=3,
            task_id=task_id
        )

    def get_incremental_guidance(
        self,
        current_progress: float,
        remaining_tasks: List[str],
        context: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Get guidance for next steps based on current progress.

        Args:
            current_progress: Progress percentage (0.0 to 1.0)
            remaining_tasks: List of remaining task descriptions
            context: Additional context
            task_id: Task identifier for tracking

        Returns:
            List of relevant guidance examples
        """
        if not remaining_tasks:
            return []

        next_task = remaining_tasks[0]
        query = f"implement {next_task} at {int(current_progress * 100)}% progress"

        return self._execute_query(
            query=query,
            query_type="incremental_guidance",
            filters=context,
            top_k=3,
            task_id=task_id
        )

    # ============================================================================
    # Internal Helper Methods
    # ============================================================================

    def _execute_query(
        self,
        query: str,
        query_type: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """Execute query against Vector DB."""
        # Check query limit
        if task_id and not self._check_query_limit(task_id):
            raise RuntimeError(
                f"Query limit exceeded for task {task_id} "
                f"(max: {self._max_queries_per_task})"
            )

        # Execute with timeout
        start_time = time.time()

        try:
            raw_results = self._vector_db.query_semantic(
                query_text=query,
                top_k=top_k,
                filters=filters
            )

            # Convert to QueryResult format
            results = [
                QueryResult(
                    content=r.get("content", ""),
                    metadata=r.get("metadata", {}),
                    similarity_score=r.get("similarity_score", 0.0),
                    query_type=query_type
                )
                for r in raw_results
            ]

            # Track query
            self._track_query(query_type, task_id, len(results))

            # Record in history
            elapsed = time.time() - start_time
            self._query_history.append({
                "query": query,
                "query_type": query_type,
                "task_id": task_id,
                "results_count": len(results),
                "elapsed_seconds": elapsed,
                "timestamp": datetime.utcnow()
            })

            return results

        except Exception as e:
            # Log error and return empty results
            print(f"Vector DB query error: {str(e)}")
            return []

    def _query_initialization(
        self,
        context: QueryContext,
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query at task initialization."""
        if context.component_type and context.language:
            return self.get_best_practices(
                component_type=context.component_type,
                language=context.language,
                task_id=task_id
            )
        return []

    def _query_checkpoint(
        self,
        context: QueryContext,
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query at periodic checkpoint."""
        remaining_tasks = context.additional_context.get("remaining_tasks", [])
        return self.get_incremental_guidance(
            current_progress=context.current_progress,
            remaining_tasks=remaining_tasks,
            context=context.additional_context,
            task_id=task_id
        )

    def _query_error(
        self,
        context: QueryContext,
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query when error occurs."""
        if context.error_info:
            return self.find_error_solutions(
                error_type=context.error_info.get("type", "unknown"),
                context=context.error_info,
                task_id=task_id
            )
        return []

    def _query_validation_fail(
        self,
        context: QueryContext,
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query when validation fails."""
        if context.validation_feedback:
            query = f"fix validation issue: {context.validation_feedback[:100]}"
            return self._execute_query(
                query=query,
                query_type="validation_fix",
                filters={"has_validation_fix": True},
                top_k=5,
                task_id=task_id
            )
        return []

    def _query_pre_validation(
        self,
        context: QueryContext,
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query before validation to check patterns."""
        code = context.additional_context.get("code", "")
        if code and context.component_type:
            return self.validate_against_patterns(
                code_snippet=code,
                component_type=context.component_type,
                task_id=task_id
            )
        return []

    def _query_general(
        self,
        context: QueryContext,
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """General query based on context."""
        query = f"guidance for {context.stage}"
        return self._execute_query(
            query=query,
            query_type="general",
            filters=context.additional_context,
            top_k=3,
            task_id=task_id
        )

    def _check_query_limit(self, task_id: str) -> bool:
        """Check if task has exceeded query limit."""
        count = self._query_counts.get(task_id, 0)
        return count < self._max_queries_per_task

    def _track_query(
        self,
        query_type: str,
        task_id: Optional[str],
        results_count: int = 0
    ):
        """Track query execution."""
        self._total_queries += 1

        if task_id:
            self._query_counts[task_id] = self._query_counts.get(task_id, 0) + 1

    # ============================================================================
    # Statistics and Monitoring
    # ============================================================================

    def get_query_stats(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get query statistics.

        Args:
            task_id: Optional task ID to filter stats

        Returns:
            Dictionary with query statistics
        """
        if task_id:
            return {
                "task_id": task_id,
                "query_count": self._query_counts.get(task_id, 0),
                "max_queries": self._max_queries_per_task,
                "remaining_queries": self._max_queries_per_task - self._query_counts.get(task_id, 0)
            }

        return {
            "total_queries": self._total_queries,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": (
                self._cache_hits / (self._cache_hits + self._cache_misses)
                if (self._cache_hits + self._cache_misses) > 0 else 0.0
            ),
            "cache_size": self._cache.size() if self._cache else 0,
            "active_tasks": len(self._query_counts),
            "query_history_size": len(self._query_history)
        }

    def get_query_history(
        self,
        task_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get query history.

        Args:
            task_id: Optional task ID to filter history
            limit: Maximum number of entries to return

        Returns:
            List of query history entries
        """
        history = self._query_history

        if task_id:
            history = [h for h in history if h.get("task_id") == task_id]

        return history[-limit:]

    def reset_task_queries(self, task_id: str):
        """Reset query count for a specific task."""
        if task_id in self._query_counts:
            del self._query_counts[task_id]

    def clear_cache(self):
        """Clear the query cache."""
        if self._cache:
            self._cache.clear()


def create_universal_vector_db_client(
    config: Optional[Dict[str, Any]] = None,
    enable_cache: bool = True,
    cache_ttl_seconds: int = 300
) -> UniversalVectorDBClient:
    """
    Factory function to create Universal Vector DB Client.

    Args:
        config: Vector DB configuration
        enable_cache: Enable query result caching
        cache_ttl_seconds: Cache time-to-live in seconds

    Returns:
        Configured UniversalVectorDBClient instance
    """
    return UniversalVectorDBClient(
        config=config,
        enable_cache=enable_cache,
        cache_ttl_seconds=cache_ttl_seconds
    )
