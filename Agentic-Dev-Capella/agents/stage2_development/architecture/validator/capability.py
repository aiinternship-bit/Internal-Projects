"""
agents/stage2_development/architect_validator/capability.py

Capability declaration for Architecture Validator Agent.
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


ARCHITECTURE_VALIDATOR_AGENT_CAPABILITY = AgentCapability(
    agent_id="architecture_validator_agent",
    agent_name="Architecture Validator Agent",
    agent_type=AgentType.VALIDATOR,

    description=(
        "Validates architecture designs for correctness, completeness, and best practices."
    ),

    capabilities={
        "architecture_validation",
        "design_review",
        "best_practices_checking"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.JSON,
        InputModality.YAML,
        InputModality.TEXT
    },

    output_types={
        "validation_report",
        "feedback",
        "recommendations"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=12,
        kb_query_triggers=["start", "error", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=12.0,
        p95_task_duration_minutes=24.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.1,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=12.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage2",
        "validation",
        "architecture"
    
)


def get_architecture_validator_capability() -> AgentCapability:
    return ARCHITECTURE_VALIDATOR_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    ARCHITECTURE_VALIDATOR_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
