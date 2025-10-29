"""
agents/orchestration/orchestrator/capability.py

Capability declaration for Orchestrator Agent.
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


ORCHESTRATOR_AGENT_CAPABILITY = AgentCapability(
    agent_id="orchestrator_agent",
    agent_name="Orchestrator Agent",
    agent_type=AgentType.ORCHESTRATOR,

    description=(
        "Main orchestrator supporting both static (stage-based) and dynamic (capability-based) modes. Central coordinator for all agents."
    ),

    capabilities={
        "task_routing",
        "agent_coordination",
        "progress_tracking",
        "error_handling"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON
    },

    output_types={
        "orchestration_plan",
        "status_updates",
        "execution_report"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=5,
        kb_query_triggers=["start", "error", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
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
        "coordinator"
    
)


def get_orchestrator_capability() -> AgentCapability:
    return ORCHESTRATOR_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    ORCHESTRATOR_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
