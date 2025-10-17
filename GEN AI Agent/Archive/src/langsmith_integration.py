"""
LangSmith Integration Module
Provides tracing and diagnostic capabilities for Excel-RAG system
"""
import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from . import config


class LangSmithTracer:
    """
    Wrapper for LangSmith tracing functionality
    Provides fallback when LangSmith is not available
    """

    def __init__(self):
        """Initialize LangSmith tracer if available"""
        self.enabled = config.is_langsmith_enabled()
        self.client = None

        if self.enabled:
            try:
                from langsmith import Client
                self.client = Client(
                    api_key=config.LANGCHAIN_API_KEY,
                    api_url=config.LANGCHAIN_ENDPOINT
                )
                print(f"✓ LangSmith tracing enabled (Project: {config.LANGCHAIN_PROJECT})")
            except ImportError:
                print("⚠ LangSmith package not installed. Install with: pip install langsmith")
                self.enabled = False
            except Exception as e:
                print(f"⚠ LangSmith initialization failed: {e}")
                self.enabled = False
        else:
            if not config.LANGCHAIN_API_KEY:
                print("ℹ LangSmith not configured (set LANGCHAIN_API_KEY in .env)")

    def trace_query(
        self,
        query: str,
        structure_results: List[Dict],
        content_results: List[Dict],
        llm_response: Dict[str, Any],
        execution_time: float
    ):
        """
        Trace a complete query execution

        Args:
            query: User query
            structure_results: Structure retrieval results
            content_results: Content retrieval results
            llm_response: LLM response
            execution_time: Total execution time in seconds
        """
        if not self.enabled or not self.client:
            return

        try:
            # Create trace data
            trace_data = {
                "name": "excel_rag_query",
                "inputs": {"query": query},
                "outputs": {
                    "answer": llm_response.get("answer", ""),
                    "model": llm_response.get("model", ""),
                    "token_usage": llm_response.get("token_usage", 0)
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "execution_time_seconds": execution_time,
                    "structure_results_count": len(structure_results),
                    "content_results_count": len(content_results),
                    "relevant_sheets": [r["sheet"] for r in structure_results],
                    "backend": llm_response.get("backend", "unknown")
                },
                "tags": ["excel-rag", "query"]
            }

            # Log to LangSmith
            self.client.create_run(
                **trace_data,
                run_type="chain",
                project_name=config.LANGCHAIN_PROJECT
            )

        except Exception as e:
            print(f"⚠ LangSmith tracing error: {e}")

    def trace_retrieval(
        self,
        query: str,
        retrieval_type: str,
        results: List[Dict],
        execution_time: float
    ):
        """
        Trace a retrieval operation (structure or content)

        Args:
            query: Query text
            retrieval_type: 'structure' or 'content'
            results: Retrieval results
            execution_time: Execution time in seconds
        """
        if not self.enabled or not self.client:
            return

        try:
            trace_data = {
                "name": f"excel_rag_{retrieval_type}_retrieval",
                "inputs": {"query": query},
                "outputs": {
                    "results_count": len(results),
                    "top_score": results[0]["score"] if results else 0.0
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "execution_time_seconds": execution_time,
                    "retrieval_type": retrieval_type
                },
                "tags": ["excel-rag", "retrieval", retrieval_type]
            }

            self.client.create_run(
                **trace_data,
                run_type="retriever",
                project_name=config.LANGCHAIN_PROJECT
            )

        except Exception as e:
            print(f"⚠ LangSmith tracing error: {e}")

    def trace_llm_call(
        self,
        prompt: str,
        response: str,
        model: str,
        token_usage: int,
        execution_time: float
    ):
        """
        Trace an LLM API call

        Args:
            prompt: Input prompt
            response: LLM response
            model: Model name
            token_usage: Number of tokens used
            execution_time: Execution time in seconds
        """
        if not self.enabled or not self.client:
            return

        try:
            trace_data = {
                "name": "excel_rag_llm_call",
                "inputs": {"prompt": prompt[:500]},  # Truncate long prompts
                "outputs": {"response": response[:500]},  # Truncate long responses
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "model": model,
                    "token_usage": token_usage,
                    "execution_time_seconds": execution_time,
                    "prompt_length": len(prompt),
                    "response_length": len(response)
                },
                "tags": ["excel-rag", "llm", model]
            }

            self.client.create_run(
                **trace_data,
                run_type="llm",
                project_name=config.LANGCHAIN_PROJECT
            )

        except Exception as e:
            print(f"⚠ LangSmith tracing error: {e}")

    def log_error(
        self,
        operation: str,
        error: Exception,
        context: Dict[str, Any] = None
    ):
        """
        Log an error to LangSmith

        Args:
            operation: Operation that failed
            error: Exception object
            context: Additional context
        """
        if not self.enabled or not self.client:
            return

        try:
            trace_data = {
                "name": f"excel_rag_error_{operation}",
                "inputs": context or {},
                "outputs": {"error": str(error)},
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(error).__name__,
                    "operation": operation
                },
                "tags": ["excel-rag", "error", operation]
            }

            self.client.create_run(
                **trace_data,
                run_type="chain",
                project_name=config.LANGCHAIN_PROJECT
            )

        except Exception as e:
            print(f"⚠ LangSmith error logging failed: {e}")


# Global tracer instance
_tracer = None

def get_tracer() -> LangSmithTracer:
    """Get or create global tracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = LangSmithTracer()
    return _tracer


# Decorator for tracing functions
def trace_function(func):
    """
    Decorator to automatically trace function execution

    Usage:
        @trace_function
        def my_function(arg1, arg2):
            ...
    """
    def wrapper(*args, **kwargs):
        tracer = get_tracer()
        if not tracer.enabled:
            return func(*args, **kwargs)

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Log successful execution
            if tracer.client:
                tracer.client.create_run(
                    name=f"excel_rag_{func.__name__}",
                    run_type="chain",
                    inputs={"args": str(args)[:200], "kwargs": str(kwargs)[:200]},
                    outputs={"result": str(result)[:200]},
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "execution_time_seconds": execution_time,
                        "function": func.__name__
                    },
                    tags=["excel-rag", "function", func.__name__],
                    project_name=config.LANGCHAIN_PROJECT
                )

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            tracer.log_error(func.__name__, e, {"args": str(args)[:200]})
            raise

    return wrapper


# Environment setup helper
def setup_langsmith_env():
    """
    Set up LangSmith environment variables if configured in config
    This ensures LangChain integrations can use LangSmith automatically
    """
    if config.is_langsmith_enabled():
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = config.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = config.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = config.LANGCHAIN_ENDPOINT
        print("✓ LangSmith environment configured")


# Initialize on import if enabled
if config.is_langsmith_enabled():
    setup_langsmith_env()
