"""
agents/stage3_cicd/root_cause_analysis/capability.py

Capability declaration for Root Cause Analysis Agent.
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


ROOT_CAUSE_ANALYSIS_AGENT_CAPABILITY = AgentCapability(
    agent_id="root_cause_analysis_agent",
    agent_name="Root Cause Analysis Agent",
    agent_type=AgentType.DEVOPS_ENGINEER,

    description=(
        "Performs root cause analysis on incidents and failures. Analyzes logs, metrics, and traces."
    ),

    capabilities={
        "rca_analysis",
        "log_analysis",
        "metric_correlation",
        "incident_investigation"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON
    },

    output_types={
        "rca_report",
        "findings",
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
        avg_task_duration_minutes=20.0,
        p95_task_duration_minutes=40.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.16,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=20.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage3",
        "rca",
        "incident"
    
)


def get_root_cause_analysis_capability() -> AgentCapability:
    return ROOT_CAUSE_ANALYSIS_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    ROOT_CAUSE_ANALYSIS_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
