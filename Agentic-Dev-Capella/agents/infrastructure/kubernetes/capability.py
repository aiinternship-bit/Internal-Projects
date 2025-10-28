"""
agents/infrastructure/kubernetes/capability.py

Capability declaration for Kubernetes Agent.
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


KUBERNETES_CAPABILITY = AgentCapability(
    agent_id="kubernetes_agent",
    agent_name="Kubernetes Agent",
    agent_type=AgentType.DEVOPS_ENGINEER,

    description=(
        "Generates Kubernetes manifests, Helm charts, and service mesh configurations. "
        "Supports K8s 1.28+, Helm 3, Istio, and various deployment strategies."
    ),

    capabilities={
        "manifest_creation",
        "helm_charts",
        "service_mesh_config",
        "deployment_strategies",
        "rbac_policies",
        "resource_optimization",
        "ingress_configuration",
        "hpa_configuration"
    },

    supported_languages=[
        "yaml",
        "helm",
        "go-template"
    ],

    supported_frameworks=[
        "kubernetes",
        "helm",
        "istio",
        "linkerd",
        "kustomize"
    ],

    supported_platforms=[
        "gke",
        "eks",
        "aks",
        "on-premise-k8s"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON,
        InputModality.YAML,
        InputModality.CODE
    },

    output_types={
        "manifests",
        "helm_chart",
        "service_mesh_config",
        "scripts",
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
        avg_task_duration_minutes=14.0,
        p95_task_duration_minutes=28.0,
        success_rate=0.89,
        avg_validation_failures=0.6,
        retry_rate=0.16
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.11,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=14.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["infrastructure", "kubernetes", "helm", "containers", "devops"]
)


def get_kubernetes_capability() -> AgentCapability:
    return KUBERNETES_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    KUBERNETES_CAPABILITY.agent_id = vertex_ai_resource_id
