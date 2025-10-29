"""
agents/stage2_development/builder/capability.py

Capability declaration for Builder Agent.
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


BUILDER_AGENT_CAPABILITY = AgentCapability(
    agent_id="builder_agent",
    agent_name="Builder Agent",
    agent_type=AgentType.DEVOPS_ENGINEER,

    description=(
        "Builds and packages modern code. Generates build scripts, Dockerfiles, and CI/CD configs."
    ),

    capabilities={
        "build_automation",
        "docker_generation",
        "ci_cd_config",
        "artifact_packaging"
    },

    supported_languages=[],

    supported_frameworks=[
        ""docker"",
        ""gradle"",
        ""maven"",
        ""npm""
    ],

    supported_platforms=[
        ""kubernetes"",
        ""cloud""
    ],

    input_modalities={
        InputModality.CODE
    },

    output_types={
        "dockerfile",
        "build_script",
        "ci_config",
        "artifacts"
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
        avg_task_duration_minutes=10.0,
        p95_task_duration_minutes=20.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.08,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=10.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage2",
        "build",
        "ci_cd"
    
)


def get_builder_capability() -> AgentCapability:
    return BUILDER_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    BUILDER_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
