"""
shared/utils/kb_integration_mixin.py

Mixin class providing dynamic knowledge base integration for all agents.
Enables intelligent, periodic KB queries at appropriate decision points.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

from shared.tools.vector_db_client import (
    UniversalVectorDBClient,
    QueryContext,
    QueryResult
)


class DynamicKnowledgeBaseIntegration:
    """
    Mixin for agents to enable smart, periodic knowledge base queries.

    Usage:
        class MyAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
            def __init__(self, context, message_bus, vector_db_client):
                super().__init__(context, message_bus)
                self.initialize_kb_integration(vector_db_client)
    """

    def initialize_kb_integration(
        self,
        vector_db_client: UniversalVectorDBClient,
        query_strategy: str = "adaptive",
        checkpoint_frequency: int = 10,
        auto_query_on_error: bool = True,
        auto_query_on_validation_fail: bool = True
    ):
        """
        Initialize KB integration for this agent.

        Args:
            vector_db_client: Universal Vector DB client instance
            query_strategy: Strategy for KB queries ("never", "minimal", "adaptive", "aggressive")
            checkpoint_frequency: Query every N operations (for "adaptive"/"aggressive")
            auto_query_on_error: Automatically query KB when errors occur
            auto_query_on_validation_fail: Automatically query KB on validation failures
        """
        self.vector_db = vector_db_client
        self._kb_query_strategy = query_strategy
        self._kb_checkpoint_frequency = checkpoint_frequency
        self._kb_auto_query_on_error = auto_query_on_error
        self._kb_auto_query_on_validation_fail = auto_query_on_validation_fail

        # Query tracking
        self._kb_last_query_time: Optional[datetime] = None
        self._kb_query_count = 0
        self._kb_operation_count = 0
        self._kb_context_hash: Optional[str] = None

        # Query results cache (for current task)
        self._kb_current_results: List[QueryResult] = []
        self._kb_best_practices_cache: Dict[str, List[QueryResult]] = {}

    # ============================================================================
    # Decision Logic: When to Query KB
    # ============================================================================

    def should_query_kb(
        self,
        context: Dict[str, Any],
        last_query_time: Optional[datetime] = None
    ) -> bool:
        """
        Decide if agent should query KB now based on strategy and context.

        Args:
            context: Current execution context
            last_query_time: Time of last query (optional, uses internal tracking)

        Returns:
            True if agent should query KB now
        """
        if self._kb_query_strategy == "never":
            return False

        if self._kb_query_strategy == "minimal":
            # Only query at task start
            return self._kb_query_count == 0

        # Get last query time
        if last_query_time is None:
            last_query_time = self._kb_last_query_time

        # Check for context changes
        context_changed = self._has_context_changed(context)

        # Check operation frequency
        checkpoint_reached = (self._kb_operation_count % self._kb_checkpoint_frequency) == 0

        if self._kb_query_strategy == "adaptive":
            # Query on:
            # 1. First operation
            # 2. Context change
            # 3. Periodic checkpoints
            # 4. Time-based (every 5 minutes)
            time_elapsed = self._get_time_since_last_query(last_query_time)

            return (
                self._kb_query_count == 0 or
                context_changed or
                checkpoint_reached or
                time_elapsed > 300  # 5 minutes
            )

        elif self._kb_query_strategy == "aggressive":
            # Query very frequently
            time_elapsed = self._get_time_since_last_query(last_query_time)

            return (
                self._kb_query_count == 0 or
                context_changed or
                checkpoint_reached or
                time_elapsed > 120  # 2 minutes
            )

        return False

    def should_query_on_error(self, error: Exception) -> bool:
        """
        Decide if agent should query KB when error occurs.

        Args:
            error: Exception that occurred

        Returns:
            True if should query KB for error solutions
        """
        return self._kb_auto_query_on_error

    def should_query_on_validation_fail(self, feedback: str) -> bool:
        """
        Decide if agent should query KB when validation fails.

        Args:
            feedback: Validation feedback message

        Returns:
            True if should query KB for validation fixes
        """
        return self._kb_auto_query_on_validation_fail

    def _has_context_changed(self, context: Dict[str, Any]) -> bool:
        """Check if context has changed significantly since last query."""
        import hashlib
        import json

        # Create hash of relevant context fields
        relevant_context = {
            "component_type": context.get("component_type"),
            "language": context.get("language"),
            "stage": context.get("stage"),
            "task_type": context.get("task_type")
        }

        context_str = json.dumps(relevant_context, sort_keys=True)
        context_hash = hashlib.md5(context_str.encode()).hexdigest()

        if self._kb_context_hash != context_hash:
            self._kb_context_hash = context_hash
            return True

        return False

    def _get_time_since_last_query(
        self,
        last_query_time: Optional[datetime]
    ) -> float:
        """Get seconds since last KB query."""
        if last_query_time is None:
            return float('inf')

        elapsed = datetime.utcnow() - last_query_time
        return elapsed.total_seconds()

    # ============================================================================
    # Query Type Selection
    # ============================================================================

    def determine_query_type(
        self,
        stage: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Determine what type of query is most relevant for current stage.

        Args:
            stage: Current execution stage
            context: Execution context

        Returns:
            Query type string
        """
        stage_to_query_type = {
            "initialization": "similar_implementations",
            "planning": "best_practices",
            "implementation": "similar_implementations",
            "checkpoint": "incremental_guidance",
            "error": "error_solution",
            "validation_fail": "validation_fix",
            "pre_validation": "pattern_validation",
            "optimization": "best_practices",
            "refactoring": "refactoring_examples",
            "completion": "pattern_validation"
        }

        return stage_to_query_type.get(stage, "similar_implementations")

    # ============================================================================
    # Execute KB Queries
    # ============================================================================

    def execute_dynamic_query(
        self,
        query_type: str,
        context: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Execute the appropriate KB query based on type and context.

        Args:
            query_type: Type of query to execute
            context: Query context
            task_id: Task identifier for tracking

        Returns:
            List of query results
        """
        self._kb_operation_count += 1
        self._kb_query_count += 1
        self._kb_last_query_time = datetime.utcnow()

        # Get task_id from context if not provided
        if task_id is None:
            task_id = context.get("task_id")

        if query_type == "similar_implementations":
            results = self._query_similar_implementations(context, task_id)
        elif query_type == "best_practices":
            results = self._query_best_practices(context, task_id)
        elif query_type == "error_solution":
            results = self._query_error_solution(context, task_id)
        elif query_type == "validation_fix":
            results = self._query_validation_fix(context, task_id)
        elif query_type == "pattern_validation":
            results = self._query_pattern_validation(context, task_id)
        elif query_type == "incremental_guidance":
            results = self._query_incremental_guidance(context, task_id)
        elif query_type == "refactoring_examples":
            results = self._query_refactoring(context, task_id)
        else:
            # Default: similar implementations
            results = self._query_similar_implementations(context, task_id)

        # Cache results
        self._kb_current_results = results

        return results

    def query_kb_at_stage(
        self,
        stage: str,
        context: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> List[QueryResult]:
        """
        Query KB at a specific execution stage with appropriate query type.

        Args:
            stage: Execution stage
            context: Context information
            task_id: Task identifier

        Returns:
            List of relevant query results
        """
        query_type = self.determine_query_type(stage, context)

        # Build QueryContext
        query_context_obj = QueryContext(
            stage=stage,
            task_id=task_id or context.get("task_id", "unknown"),
            component_type=context.get("component_type"),
            language=context.get("language"),
            current_progress=context.get("progress", 0.0),
            additional_context=context
        )

        # Execute via Vector DB client
        results = self.vector_db.query_at_checkpoint(
            context=query_context_obj,
            task_id=task_id
        )

        self._kb_query_count += 1
        self._kb_last_query_time = datetime.utcnow()

        return results

    # ============================================================================
    # Specific Query Implementations
    # ============================================================================

    def _query_similar_implementations(
        self,
        context: Dict[str, Any],
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query for similar code implementations."""
        query = context.get("query", "")
        if not query:
            component_type = context.get("component_type", "")
            language = context.get("language", "")
            query = f"implement {component_type} in {language}"

        filters = {
            "component_type": context.get("component_type"),
            "language": context.get("language")
        }

        return self.vector_db.search_similar_implementations(
            query=query,
            filters={k: v for k, v in filters.items() if v},
            top_k=5,
            task_id=task_id
        )

    def _query_best_practices(
        self,
        context: Dict[str, Any],
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query for best practices."""
        component_type = context.get("component_type", "component")
        language = context.get("language", "python")

        # Check cache first
        cache_key = f"{component_type}_{language}"
        if cache_key in self._kb_best_practices_cache:
            return self._kb_best_practices_cache[cache_key]

        results = self.vector_db.get_best_practices(
            component_type=component_type,
            language=language,
            task_id=task_id
        )

        # Cache results
        self._kb_best_practices_cache[cache_key] = results

        return results

    def _query_error_solution(
        self,
        context: Dict[str, Any],
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query for error solutions."""
        error_info = context.get("error_info", {})
        error_type = error_info.get("type", "unknown")

        return self.vector_db.find_error_solutions(
            error_type=error_type,
            context=error_info,
            task_id=task_id
        )

    def _query_validation_fix(
        self,
        context: Dict[str, Any],
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query for validation fixes."""
        feedback = context.get("validation_feedback", "")

        query_context = QueryContext(
            stage="validation_fail",
            task_id=task_id or "unknown",
            validation_feedback=feedback,
            additional_context=context
        )

        return self.vector_db.query_at_checkpoint(query_context, task_id)

    def _query_pattern_validation(
        self,
        context: Dict[str, Any],
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query for pattern validation."""
        code = context.get("code", "")
        component_type = context.get("component_type", "")

        return self.vector_db.validate_against_patterns(
            code_snippet=code,
            component_type=component_type,
            task_id=task_id
        )

    def _query_incremental_guidance(
        self,
        context: Dict[str, Any],
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query for incremental guidance."""
        progress = context.get("progress", 0.0)
        remaining_tasks = context.get("remaining_tasks", [])

        return self.vector_db.get_incremental_guidance(
            current_progress=progress,
            remaining_tasks=remaining_tasks,
            context=context,
            task_id=task_id
        )

    def _query_refactoring(
        self,
        context: Dict[str, Any],
        task_id: Optional[str]
    ) -> List[QueryResult]:
        """Query for refactoring examples."""
        anti_pattern = context.get("anti_pattern", "")
        language = context.get("language", "")

        query = f"refactor {anti_pattern} in {language}"

        return self.vector_db.search_similar_implementations(
            query=query,
            filters={"is_refactoring_example": True},
            top_k=3,
            task_id=task_id
        )

    # ============================================================================
    # Integrate KB Results
    # ============================================================================

    def integrate_kb_results(
        self,
        results: List[QueryResult],
        current_work: Any
    ) -> Dict[str, Any]:
        """
        Merge KB findings into ongoing work.

        Args:
            results: Query results from KB
            current_work: Current work in progress

        Returns:
            Dictionary with integration suggestions
        """
        if not results:
            return {"suggestions": [], "confidence": 0.0}

        # Extract relevant patterns and suggestions
        suggestions = []
        confidence_scores = []

        for result in results:
            suggestion = {
                "content": result.content,
                "metadata": result.metadata,
                "similarity": result.similarity_score,
                "applicable": self._is_result_applicable(result, current_work)
            }
            suggestions.append(suggestion)
            confidence_scores.append(result.similarity_score)

        # Calculate overall confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return {
            "suggestions": suggestions,
            "confidence": avg_confidence,
            "count": len(suggestions),
            "best_match": suggestions[0] if suggestions else None
        }

    def _is_result_applicable(
        self,
        result: QueryResult,
        current_work: Any
    ) -> bool:
        """Check if query result is applicable to current work."""
        # Simple heuristic: high similarity score means applicable
        return result.similarity_score > 0.7

    # ============================================================================
    # Statistics and Monitoring
    # ============================================================================

    def get_kb_stats(self) -> Dict[str, Any]:
        """
        Get KB integration statistics for this agent instance.

        Returns:
            Dictionary with KB usage statistics
        """
        return {
            "query_count": self._kb_query_count,
            "operation_count": self._kb_operation_count,
            "queries_per_operation": (
                self._kb_query_count / self._kb_operation_count
                if self._kb_operation_count > 0 else 0.0
            ),
            "last_query_time": self._kb_last_query_time,
            "strategy": self._kb_query_strategy,
            "checkpoint_frequency": self._kb_checkpoint_frequency,
            "cached_results_count": len(self._kb_current_results),
            "cached_best_practices_count": len(self._kb_best_practices_cache)
        }

    def reset_kb_stats(self):
        """Reset KB statistics for this agent."""
        self._kb_query_count = 0
        self._kb_operation_count = 0
        self._kb_last_query_time = None
        self._kb_current_results = []
        self._kb_best_practices_cache = {}

    def increment_operation_count(self):
        """Increment operation counter (call this for each operation performed)."""
        self._kb_operation_count += 1
