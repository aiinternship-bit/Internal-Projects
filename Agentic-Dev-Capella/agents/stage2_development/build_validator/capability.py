"""
agents/stage2_development/build_validator/capability.py

Capability declaration for Build Validator Agent.
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


BUILD_VALIDATOR_AGENT_CAPABILITY = AgentCapability(
    agent_id="build_validator_agent",
    agent_name="Build Validator Agent",
    agent_type=AgentType.VALIDATOR,

    description=(
        "Validates build artifacts for completeness, dependencies, and packaging."
    ),

    capabilities={
        "build_validation",
        "artifact_verification",
        "dependency_checking"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.CODE,
        InputModality.JSON
    },

    output_types={
        "validation_report",
        "build_status",
        "errors"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=False,
        kb_query_strategy=KBQueryStrategy.MINIMAL,
        kb_query_frequency=5,
        kb_query_triggers=[],
        max_kb_queries_per_task=10,
        enable_kb_caching=False,
        kb_cache_ttl_seconds=60
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=8.0,
        p95_task_duration_minutes=16.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.06,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=8.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage2",
        "validation",
        "build"
    
)


def get_build_validator_capability() -> AgentCapability:
    return BUILD_VALIDATOR_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    BUILD_VALIDATOR_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
