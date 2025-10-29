"""
agents/orchestration/telemetry/capability.py

Capability declaration for Telemetry Audit Agent.
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


TELEMETRY_AUDIT_AGENT_CAPABILITY = AgentCapability(
    agent_id="telemetry_audit_agent",
    agent_name="Telemetry Audit Agent",
    agent_type=AgentType.ORCHESTRATOR,

    description=(
        "Tracks all system activities for audit and compliance. Creates comprehensive audit trails."
    ),

    capabilities={
        "activity_tracking",
        "audit_logging",
        "compliance_reporting"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.JSON
    },

    output_types={
        "audit_log",
        "activity_report",
        "compliance_data"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=False,
        kb_query_strategy=KBQueryStrategy.MINIMAL,
        kb_query_frequency=1,
        kb_query_triggers=[],
        max_kb_queries_per_task=10,
        enable_kb_caching=False,
        kb_cache_ttl_seconds=60
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=2.0,
        p95_task_duration_minutes=4.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.02,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=2.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "orchestration",
        "audit",
        "telemetry"
    
)


def get_telemetry_audit_capability() -> AgentCapability:
    return TELEMETRY_AUDIT_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    TELEMETRY_AUDIT_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
