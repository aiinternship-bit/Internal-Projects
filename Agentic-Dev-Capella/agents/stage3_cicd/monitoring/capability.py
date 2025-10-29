"""
agents/stage3_cicd/monitoring/capability.py

Capability declaration for Monitoring Agent.
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


MONITORING_AGENT_CAPABILITY = AgentCapability(
    agent_id="monitoring_agent",
    agent_name="Monitoring Agent",
    agent_type=AgentType.DEVOPS_ENGINEER,

    description=(
        "Sets up monitoring, alerting, and observability. Configures Prometheus, Grafana, and Cloud Monitoring."
    ),

    capabilities={
        "monitoring_setup",
        "alerting_config",
        "dashboard_creation",
        "slo_definition"
    },

    supported_languages=[],

    supported_frameworks=[
        ""prometheus"",
        ""grafana"",
        ""cloud-monitoring""
    ],

    supported_platforms=[
        ""kubernetes"",
        ""cloud""
    ],

    input_modalities={
        InputModality.YAML,
        InputModality.JSON
    },

    output_types={
        "monitoring_config",
        "dashboards",
        "alert_rules"
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
        avg_task_duration_minutes=15.0,
        p95_task_duration_minutes=30.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.12,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=15.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage3",
        "monitoring",
        "observability"
    
)


def get_monitoring_capability() -> AgentCapability:
    return MONITORING_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    MONITORING_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
