"""
agents/stage0_discovery/domain_expert/capability.py

Capability declaration for Domain Expert Agent.
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


DOMAIN_EXPERT_AGENT_CAPABILITY = AgentCapability(
    agent_id="domain_expert_agent",
    agent_name="Domain Expert Agent",
    agent_type=AgentType.LEGACY_MODERNIZATION,

    description=(
        "Infers business domain from legacy code analysis. Identifies domain patterns and business logic."
    ),

    capabilities={
        "domain_inference",
        "business_logic_identification",
        "pattern_recognition"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE
    },

    output_types={
        "domain_model",
        "business_rules",
        "glossary"
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
        "stage0",
        "discovery",
        "domain"
    
)


def get_domain_expert_capability() -> AgentCapability:
    return DOMAIN_EXPERT_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    DOMAIN_EXPERT_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
