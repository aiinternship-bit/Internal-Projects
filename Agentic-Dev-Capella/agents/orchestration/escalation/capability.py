"""
agents/orchestration/escalation/capability.py

Capability declaration for Escalation Agent.
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


ESCALATION_AGENT_CAPABILITY = AgentCapability(
    agent_id="escalation_agent",
    agent_name="Escalation Agent",
    agent_type=AgentType.ORCHESTRATOR,

    description=(
        "Handles escalations after validation failures. Routes to human review when automated resolution fails."
    ),

    capabilities={
        "escalation_handling",
        "human_routing",
        "deadlock_resolution"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON
    },

    output_types={
        "escalation_report",
        "resolution_plan"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=False,
        kb_query_strategy=KBQueryStrategy.MINIMAL,
        kb_query_frequency=3,
        kb_query_triggers=[],
        max_kb_queries_per_task=10,
        enable_kb_caching=False,
        kb_cache_ttl_seconds=60
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=5.0,
        p95_task_duration_minutes=10.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.04,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=5.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "orchestration",
        "escalation"
    
)


def get_escalation_capability() -> AgentCapability:
    return ESCALATION_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    ESCALATION_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
