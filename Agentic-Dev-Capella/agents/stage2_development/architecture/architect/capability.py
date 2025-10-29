"""
agents/stage2_development/technical_architect/capability.py

Capability declaration for Technical Architect Agent.
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


TECHNICAL_ARCHITECT_AGENT_CAPABILITY = AgentCapability(
    agent_id="technical_architect_agent",
    agent_name="Technical Architect Agent",
    agent_type=AgentType.BACKEND_ENGINEER,

    description=(
        "Designs modern architecture from legacy code analysis. Creates microservices, APIs, and data models."
    ),

    capabilities={
        "architecture_design",
        "microservices_decomposition",
        "api_design",
        "data_modeling"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON,
        InputModality.CODE
    },

    output_types={
        "architecture_spec",
        "component_design",
        "api_spec"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=15,
        kb_query_triggers=["start", "error", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=30.0,
        p95_task_duration_minutes=60.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.24,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=30.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage2",
        "architecture",
        "design"
    
)


def get_technical_architect_capability() -> AgentCapability:
    return TECHNICAL_ARCHITECT_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    TECHNICAL_ARCHITECT_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
