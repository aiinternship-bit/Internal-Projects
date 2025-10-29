"""
agents/stage2_development/code_validator/capability.py

Capability declaration for Code Validator Agent.
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


CODE_VALIDATOR_AGENT_CAPABILITY = AgentCapability(
    agent_id="code_validator_agent",
    agent_name="Code Validator Agent",
    agent_type=AgentType.VALIDATOR,

    description=(
        "Validates generated code for correctness, syntax, and functional requirements."
    ),

    capabilities={
        "code_validation",
        "syntax_checking",
        "functional_verification"
    },

    supported_languages=[
        ""python"",
        ""typescript"",
        ""java"",
        ""go""
    ],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.CODE
    },

    output_types={
        "validation_report",
        "feedback",
        "errors"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,
        kb_query_triggers=["start", "error", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=10.0,
        p95_task_duration_minutes=20.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.08,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=10.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage2",
        "validation",
        "code"
    
)


def get_code_validator_capability() -> AgentCapability:
    return CODE_VALIDATOR_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    CODE_VALIDATOR_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
