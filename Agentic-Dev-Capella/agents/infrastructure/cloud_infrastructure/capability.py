"""
agents/infrastructure/cloud_infrastructure/capability.py

Capability declaration for Cloud Infrastructure Agent.
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


CLOUD_INFRASTRUCTURE_CAPABILITY = AgentCapability(
    agent_id="cloud_infrastructure_agent",
    agent_name="Cloud Infrastructure Agent",
    agent_type=AgentType.DEVOPS_ENGINEER,

    description=(
        "Generates Infrastructure as Code (IaC) for multi-cloud deployments. "
        "Supports Terraform, CloudFormation, and GCP Deployment Manager across GCP, AWS, and Azure."
    ),

    capabilities={
        "terraform_development",
        "cloudformation_development",
        "gcp_deployment_manager",
        "multi_cloud_setup",
        "cost_optimization",
        "security_hardening",
        "disaster_recovery"
    },

    supported_languages=[
        "hcl",  # Terraform
        "yaml",
        "json"
    ],

    supported_frameworks=[
        "terraform",
        "cloudformation",
        "gcp-deployment-manager",
        "pulumi"
    ],

    supported_platforms=[
        "gcp",
        "aws",
        "azure",
        "multi-cloud"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON,
        InputModality.YAML,
        InputModality.PDF
    },

    output_types={
        "terraform",
        "cloudformation",
        "deployment_manager",
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
        avg_task_duration_minutes=16.0,
        p95_task_duration_minutes=32.0,
        success_rate=0.88,
        avg_validation_failures=0.7,
        retry_rate=0.18
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.13,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=16.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["infrastructure", "iac", "terraform", "cloud", "devops"]
)


def get_cloud_infrastructure_capability() -> AgentCapability:
    return CLOUD_INFRASTRUCTURE_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    CLOUD_INFRASTRUCTURE_CAPABILITY.agent_id = vertex_ai_resource_id
