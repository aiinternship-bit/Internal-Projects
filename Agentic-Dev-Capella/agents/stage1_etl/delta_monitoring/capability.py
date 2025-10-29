"""
agents/stage1_etl/delta_monitoring/capability.py

Capability declaration for Delta Monitoring Agent.
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


DELTA_MONITORING_AGENT_CAPABILITY = AgentCapability(
    agent_id="delta_monitoring_agent",
    agent_name="Delta Monitoring Agent",
    agent_type=AgentType.LEGACY_MODERNIZATION,

    description=(
        "Monitors changes in legacy codebase during modernization. Tracks deltas and updates knowledge base."
    ),

    capabilities={
        "change_detection",
        "diff_analysis",
        "incremental_updates"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.CODE
    },

    output_types={
        "change_report",
        "diff",
        "updates"
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
        "stage1",
        "etl",
        "monitoring"
    
)


def get_delta_monitoring_capability() -> AgentCapability:
    return DELTA_MONITORING_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    DELTA_MONITORING_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
