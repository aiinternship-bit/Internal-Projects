"""
agents/infrastructure/observability/capability.py

Capability declaration for Observability Agent.
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


OBSERVABILITY_CAPABILITY = AgentCapability(
    agent_id="observability_agent",
    agent_name="Observability Agent",
    agent_type=AgentType.DEVOPS_ENGINEER,

    description=(
        "Sets up comprehensive observability with monitoring, alerting, and distributed tracing. "
        "Supports Prometheus, Grafana, Jaeger, Google Cloud Monitoring, and OpenTelemetry."
    ),

    capabilities={
        "prometheus_setup",
        "grafana_dashboards",
        "distributed_tracing",
        "slo_sli_definition",
        "alert_configuration",
        "log_aggregation",
        "opentelemetry_instrumentation",
        "metrics_collection"
    },

    supported_languages=[
        "yaml",
        "json",
        "promql"
    ],

    supported_frameworks=[
        "prometheus",
        "grafana",
        "jaeger",
        "opentelemetry",
        "cloud-monitoring",
        "elk-stack"
    ],

    supported_platforms=[
        "kubernetes",
        "cloud",
        "on-premise"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON,
        InputModality.YAML,
        InputModality.CODE
    },

    output_types={
        "configuration",
        "dashboards",
        "alert_rules",
        "instrumentation_code",
        "documentation"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,
        kb_query_triggers=["start", "error", "validation_fail", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=13.0,
        p95_task_duration_minutes=26.0,
        success_rate=0.90,
        avg_validation_failures=0.5,
        retry_rate=0.14
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.10,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=13.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["infrastructure", "observability", "monitoring", "tracing", "devops"]
)


def get_observability_capability() -> AgentCapability:
    return OBSERVABILITY_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    OBSERVABILITY_CAPABILITY.agent_id = vertex_ai_resource_id
