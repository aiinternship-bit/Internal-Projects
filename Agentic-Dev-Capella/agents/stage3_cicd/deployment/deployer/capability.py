"""
agents/stage3_cicd/deployment/capability.py

Capability declaration for Deployment Agent.
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


DEPLOYMENT_AGENT_CAPABILITY = AgentCapability(
    agent_id="deployment_agent",
    agent_name="Deployment Agent",
    agent_type=AgentType.DEVOPS_ENGINEER,

    description=(
        "Deploys services to cloud platforms. Manages Kubernetes deployments and cloud resources."
    ),

    capabilities={
        "deployment_automation",
        "kubernetes_deployment",
        "cloud_provisioning"
    },

    supported_languages=[],

    supported_frameworks=[
        ""kubernetes"",
        ""terraform"",
        ""helm""
    ],

    supported_platforms=[
        ""gcp"",
        ""aws"",
        ""azure"",
        ""kubernetes""
    ],

    input_modalities={
        InputModality.YAML,
        InputModality.JSON
    },

    output_types={
        "deployment_manifest",
        "deployment_status",
        "logs"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=8,
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
        "stage3",
        "deployment",
        "devops"
    
)


def get_deployment_capability() -> AgentCapability:
    return DEPLOYMENT_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    DEPLOYMENT_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
