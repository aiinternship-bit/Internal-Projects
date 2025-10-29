"""
agents/stage2_development/multi_service_coordinator/capability.py

Capability declaration for Multi Service Coordinator Agent.
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


MULTI_SERVICE_COORDINATOR_AGENT_CAPABILITY = AgentCapability(
    agent_id="multi_service_coordinator_agent",
    agent_name="Multi Service Coordinator Agent",
    agent_type=AgentType.BACKEND_ENGINEER,

    description=(
        "Coordinates deployment of multiple services. Manages dependencies and orchestrates rollout."
    ),

    capabilities={
        "service_orchestration",
        "dependency_management",
        "rollout_coordination"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[
        ""kubernetes"",
        ""cloud""
    ],

    input_modalities={
        InputModality.JSON,
        InputModality.YAML
    },

    output_types={
        "deployment_plan",
        "orchestration_config",
        "status"
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
        "stage2",
        "coordination",
        "deployment"
    
)


def get_multi_service_coordinator_capability() -> AgentCapability:
    return MULTI_SERVICE_COORDINATOR_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    MULTI_SERVICE_COORDINATOR_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
