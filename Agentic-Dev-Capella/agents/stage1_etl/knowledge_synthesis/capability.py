"""
agents/stage1_etl/knowledge_synthesis/capability.py

Capability declaration for Knowledge Synthesis Agent.
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


KNOWLEDGE_SYNTHESIS_AGENT_CAPABILITY = AgentCapability(
    agent_id="knowledge_synthesis_agent",
    agent_name="Knowledge Synthesis Agent",
    agent_type=AgentType.LEGACY_MODERNIZATION,

    description=(
        "Synthesizes knowledge from all ETL sources. Creates Vector Search index for semantic code search."
    ),

    capabilities={
        "knowledge_synthesis",
        "vector_embeddings",
        "semantic_indexing"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.JSON
    },

    output_types={
        "vector_index",
        "knowledge_graph",
        "embeddings"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ALWAYS_QUERY,
        kb_query_frequency=20,
        kb_query_triggers=["start", "error", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=25.0,
        p95_task_duration_minutes=50.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.2,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=25.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage1",
        "etl",
        "synthesis"
    
)


def get_knowledge_synthesis_capability() -> AgentCapability:
    return KNOWLEDGE_SYNTHESIS_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    KNOWLEDGE_SYNTHESIS_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
