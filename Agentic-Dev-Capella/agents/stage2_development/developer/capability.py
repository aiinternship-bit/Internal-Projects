"""
agents/stage2_development/developer/capability.py

Capability declaration for Developer Agent.

This file defines the agent's capabilities, supported technologies,
input modalities, performance baselines, and KB integration strategy.
"""

from shared.models.agent_capability import (
    AgentCapability,
    AgentType,
    InputModality,
    KBQueryStrategy,
    KBIntegrationConfig,
    PerformanceMetrics,
    CostMetrics
)


# Developer Agent Capability Declaration
DEVELOPER_AGENT_CAPABILITY = AgentCapability(
    # Identity
    agent_id="developer_agent",  # Will be updated with Vertex AI resource ID after deployment
    agent_name="Developer Agent",
    agent_type=AgentType.DEVELOPMENT,

    # Description
    description=(
        "Implements code according to architectural specifications. "
        "Handles both new code creation and refactoring while preserving business logic. "
        "Queries knowledge base for similar implementations and best practices."
    ),

    # Capabilities
    capabilities={
        "code_implementation",
        "code_refactoring",
        "business_logic_preservation",
        "api_development",
        "database_integration",
        "error_handling",
        "logging_implementation",
        "unit_test_writing",
        "documentation_generation"
    },

    # Supported languages
    supported_languages=[
        "python",
        "typescript",
        "javascript",
        "java",
        "cpp",
        "go"
    ],

    # Supported frameworks
    supported_frameworks=[
        "fastapi",
        "django",
        "flask",
        "express",
        "react",
        "vue",
        "spring_boot",
        "gin"
    ],

    # Input modalities
    input_modalities={
        InputModality.TEXT,  # Task descriptions
        InputModality.CODE,  # Architectural specs, legacy code
        InputModality.JSON,  # Component specifications
        InputModality.YAML   # Configuration
    },

    # Output types
    output_types={
        "code",
        "tests",
        "documentation",
        "api_specs"
    },

    # Knowledge Base Integration
    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,  # Query every 10 operations
        kb_query_triggers=[
            "start",            # Query at task start for similar implementations
            "error",            # Query on implementation errors
            "validation_fail",  # Query when code validation fails
            "checkpoint"        # Query at periodic checkpoints
        ],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    # Performance Metrics (initial baselines)
    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=20.0,  # Baseline: 20 minutes per component
        p95_task_duration_minutes=45.0,   # 95th percentile
        success_rate=0.85,  # 85% success rate baseline
        avg_validation_failures=1.2,  # Average retries before validation passes
        retry_rate=0.30  # 30% of tasks require retry
    ),

    # Cost Metrics (initial estimates)
    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.15,  # ~$0.15 per component implementation
        kb_query_cost_usd=0.002,     # ~$0.002 per KB query
        total_cost_usd=0.0
    ),

    # Resource limits
    max_concurrent_tasks=3,
    estimated_task_duration_minutes=20.0,

    # Additional metadata
    version="1.0.0",
    deployment_region="us-central1",
    tags=["development", "code-generation", "refactoring", "legacy-modernization"]
)


def get_developer_capability() -> AgentCapability:
    """
    Get the Developer Agent capability declaration.

    Returns:
        AgentCapability object
    """
    return DEVELOPER_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    """
    Update the agent_id with the actual Vertex AI resource ID after deployment.

    Args:
        vertex_ai_resource_id: Full Vertex AI resource name
    """
    DEVELOPER_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
