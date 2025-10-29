"""
agents/stage1_etl/documentation_mining/capability.py

Capability declaration for Documentation Mining Agent.
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


DOCUMENTATION_MINING_AGENT_CAPABILITY = AgentCapability(
    agent_id="documentation_mining_agent",
    agent_name="Documentation Mining Agent",
    agent_type=AgentType.LEGACY_MODERNIZATION,

    description=(
        "Extracts and analyzes documentation from legacy codebase. Mines comments, READMEs, and external docs."
    ),

    capabilities={
        "documentation_extraction",
        "comment_analysis",
        "knowledge_extraction"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.PDF
    },

    output_types={
        "documentation",
        "knowledge_base",
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
        avg_task_duration_minutes=18.0,
        p95_task_duration_minutes=36.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.14,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=18.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage1",
        "etl",
        "documentation"
    
)


def get_documentation_mining_capability() -> AgentCapability:
    return DOCUMENTATION_MINING_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    DOCUMENTATION_MINING_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
