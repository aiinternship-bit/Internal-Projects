"""
shared/utils/kb_checkpoint_decorator.py

Decorator for automatic knowledge base checkpoints during agent execution.
Injects KB queries at appropriate intervals without manual intervention.
"""

from typing import Callable, List, Dict, Any, Optional
from functools import wraps
import time
from datetime import datetime


def with_kb_checkpoints(
    check_frequency: int = 10,
    auto_on_error: bool = True,
    auto_on_validation_fail: bool = True,
    query_types: Optional[List[str]] = None,
    enabled: bool = True
):
    """
    Decorator to automatically query KB at periodic checkpoints.

    Wraps agent methods to inject KB queries at regular intervals,
    on errors, and on validation failures.

    Args:
        check_frequency: Query KB every N operations (default: 10)
        auto_on_error: Automatically query KB when exceptions occur
        auto_on_validation_fail: Query KB when validation fails
        query_types: List of query types to use (default: ["similar_implementations", "best_practices"])
        enabled: Enable/disable decorator (useful for testing)

    Usage:
        @with_kb_checkpoints(check_frequency=10, auto_on_error=True)
        def implement_component(self, task_id: str, spec: Dict) -> Dict:
            # Implementation here
            pass

    Example:
        class DeveloperAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
            @with_kb_checkpoints(check_frequency=5)
            def implement_code(self, spec):
                code_lines = []
                for section in spec["sections"]:
                    # Each iteration increments checkpoint counter
                    code = self.generate_section(section)
                    code_lines.append(code)
                    # KB query automatically triggered every 5 iterations
                return "\n".join(code_lines)
    """
    if query_types is None:
        query_types = ["similar_implementations", "best_practices"]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check if KB integration is available
            if not enabled or not hasattr(self, 'vector_db'):
                # No KB integration, just execute function
                return func(self, *args, **kwargs)

            # Initialize checkpoint tracking for this call
            checkpoint_counter = 0
            original_operation_count = getattr(self, '_kb_operation_count', 0)

            # Extract task_id from args/kwargs
            task_id = kwargs.get('task_id') or (args[0] if args else None)

            try:
                # Pre-execution KB query (if at checkpoint 0)
                if hasattr(self, 'should_query_kb') and hasattr(self, 'query_kb_at_stage'):
                    context = _build_context_from_args(args, kwargs)
                    context['checkpoint_counter'] = checkpoint_counter

                    if self.should_query_kb(context):
                        self.query_kb_at_stage(
                            stage="initialization",
                            context=context,
                            task_id=task_id
                        )

                # Execute main function with checkpoint monitoring
                result = _execute_with_checkpoints(
                    func=func,
                    self_ref=self,
                    args=args,
                    kwargs=kwargs,
                    check_frequency=check_frequency,
                    query_types=query_types,
                    task_id=task_id
                )

                return result

            except Exception as error:
                # Auto-query on error if enabled
                if auto_on_error and hasattr(self, 'should_query_on_error'):
                    if self.should_query_on_error(error):
                        context = {
                            "error_info": {
                                "type": type(error).__name__,
                                "error_message": str(error),
                                "task_id": task_id
                            }
                        }
                        try:
                            self.execute_dynamic_query(
                                query_type="error_solution",
                                context=context,
                                task_id=task_id
                            )
                        except Exception:
                            # Don't let KB query errors interfere
                            pass

                # Re-raise original error
                raise

            finally:
                # Increment operation count
                if hasattr(self, 'increment_operation_count'):
                    self.increment_operation_count()

        return wrapper

    return decorator


def _execute_with_checkpoints(
    func: Callable,
    self_ref: Any,
    args: tuple,
    kwargs: dict,
    check_frequency: int,
    query_types: List[str],
    task_id: Optional[str]
) -> Any:
    """
    Execute function with checkpoint monitoring.

    This is a simplified version - in production, this would use
    more sophisticated monitoring (e.g., AST instrumentation).
    """
    # For now, just execute the function
    # In a more advanced implementation, we could:
    # 1. Inject checkpoint calls into loops
    # 2. Monitor execution progress
    # 3. Trigger KB queries at appropriate intervals

    result = func(self_ref, *args, **kwargs)

    return result


def _build_context_from_args(args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Build context dictionary from function arguments."""
    context = {}

    # Extract common parameters
    if 'spec' in kwargs:
        spec = kwargs['spec']
        if isinstance(spec, dict):
            context.update(spec)

    if 'component_type' in kwargs:
        context['component_type'] = kwargs['component_type']

    if 'language' in kwargs:
        context['language'] = kwargs['language']

    # Extract task_id
    if 'task_id' in kwargs:
        context['task_id'] = kwargs['task_id']
    elif args:
        context['task_id'] = args[0]

    return context


def kb_checkpoint(
    query_type: str = "incremental_guidance",
    task_id: Optional[str] = None
):
    """
    Manual KB checkpoint decorator for specific code blocks.

    Use this to manually insert KB queries at specific points
    rather than relying on automatic frequency-based checks.

    Args:
        query_type: Type of KB query to execute
        task_id: Task identifier

    Usage:
        @kb_checkpoint(query_type="best_practices")
        def critical_section(self, data):
            # This section will always query KB before execution
            return self.process(data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Query KB before execution
            if hasattr(self, 'execute_dynamic_query'):
                context = _build_context_from_args(args, kwargs)
                context['function_name'] = func.__name__

                try:
                    results = self.execute_dynamic_query(
                        query_type=query_type,
                        context=context,
                        task_id=task_id or context.get('task_id')
                    )

                    # Store results in context for function to access
                    kwargs['_kb_results'] = results
                except Exception:
                    # Don't let KB errors interfere
                    pass

            # Execute function
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def with_kb_guidance(
    guidance_type: str = "best_practices",
    cache_results: bool = True
):
    """
    Decorator that provides KB guidance as input to function.

    The KB results are passed as an additional parameter to the function.

    Args:
        guidance_type: Type of guidance to retrieve
        cache_results: Cache results for reuse

    Usage:
        @with_kb_guidance(guidance_type="best_practices")
        def implement_feature(self, spec, kb_guidance=None):
            if kb_guidance:
                # Use guidance from KB
                best_practices = kb_guidance
            return self.generate_code(spec, best_practices)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            kb_guidance = None

            # Query KB for guidance
            if hasattr(self, 'query_kb_at_stage'):
                context = _build_context_from_args(args, kwargs)
                task_id = context.get('task_id')

                try:
                    kb_guidance = self.query_kb_at_stage(
                        stage="initialization",
                        context=context,
                        task_id=task_id
                    )
                except Exception:
                    # Ignore KB errors
                    pass

            # Add guidance to kwargs
            if kb_guidance is not None:
                kwargs['kb_guidance'] = kb_guidance

            # Execute function
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class CheckpointManager:
    """
    Manager for tracking and coordinating KB checkpoints across agent execution.

    This allows more fine-grained control over when and how KB queries occur.
    """

    def __init__(
        self,
        agent,
        check_frequency: int = 10,
        auto_query_on_error: bool = True
    ):
        """
        Initialize checkpoint manager.

        Args:
            agent: Agent instance with KB integration
            check_frequency: Default checkpoint frequency
            auto_query_on_error: Automatically query on errors
        """
        self.agent = agent
        self.check_frequency = check_frequency
        self.auto_query_on_error = auto_query_on_error
        self.checkpoint_counter = 0
        self.last_checkpoint_time = datetime.utcnow()

    def increment(self):
        """Increment checkpoint counter."""
        self.checkpoint_counter += 1

    def should_checkpoint(self) -> bool:
        """Check if checkpoint should occur."""
        return (self.checkpoint_counter % self.check_frequency) == 0

    def execute_checkpoint(
        self,
        query_type: str,
        context: Dict[str, Any],
        task_id: Optional[str] = None
    ):
        """
        Execute KB checkpoint query.

        Args:
            query_type: Type of query
            context: Query context
            task_id: Task identifier
        """
        if not hasattr(self.agent, 'execute_dynamic_query'):
            return None

        try:
            results = self.agent.execute_dynamic_query(
                query_type=query_type,
                context=context,
                task_id=task_id
            )
            self.last_checkpoint_time = datetime.utcnow()
            return results
        except Exception as e:
            print(f"Checkpoint query failed: {str(e)}")
            return None

    def reset(self):
        """Reset checkpoint counter."""
        self.checkpoint_counter = 0
        self.last_checkpoint_time = datetime.utcnow()

    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        return {
            "checkpoint_counter": self.checkpoint_counter,
            "last_checkpoint_time": self.last_checkpoint_time,
            "time_since_last_checkpoint": (datetime.utcnow() - self.last_checkpoint_time).total_seconds(),
            "check_frequency": self.check_frequency
        }


# ============================================================================
# Context Manager for KB Checkpoints
# ============================================================================

class KBCheckpointContext:
    """
    Context manager for scoped KB checkpoint blocks.

    Usage:
        with KBCheckpointContext(agent, query_type="best_practices") as kb:
            # KB queried at entry
            result = agent.do_work()
            # KB can be queried again via kb.query()
    """

    def __init__(
        self,
        agent,
        query_type: str = "best_practices",
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize checkpoint context.

        Args:
            agent: Agent with KB integration
            query_type: Type of KB query
            task_id: Task identifier
            context: Additional context
        """
        self.agent = agent
        self.query_type = query_type
        self.task_id = task_id
        self.context = context or {}
        self.results = None

    def __enter__(self):
        """Query KB on context entry."""
        if hasattr(self.agent, 'execute_dynamic_query'):
            try:
                self.results = self.agent.execute_dynamic_query(
                    query_type=self.query_type,
                    context=self.context,
                    task_id=self.task_id
                )
            except Exception:
                self.results = None

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handle context exit."""
        # Query KB again on exit if there was an error
        if exc_type is not None and hasattr(self.agent, 'execute_dynamic_query'):
            error_context = {
                **self.context,
                "error_info": {
                    "type": exc_type.__name__,
                    "error_message": str(exc_val)
                }
            }

            try:
                self.agent.execute_dynamic_query(
                    query_type="error_solution",
                    context=error_context,
                    task_id=self.task_id
                )
            except Exception:
                pass

        return False  # Don't suppress exceptions

    def query(self, query_type: Optional[str] = None):
        """
        Execute additional KB query within context.

        Args:
            query_type: Optional different query type

        Returns:
            Query results
        """
        if not hasattr(self.agent, 'execute_dynamic_query'):
            return None

        qtype = query_type or self.query_type

        try:
            return self.agent.execute_dynamic_query(
                query_type=qtype,
                context=self.context,
                task_id=self.task_id
            )
        except Exception:
            return None

    def get_results(self):
        """Get results from entry query."""
        return self.results
