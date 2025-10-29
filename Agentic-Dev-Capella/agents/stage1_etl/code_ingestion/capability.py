"""
agents/stage1_etl/code_ingestion/capability.py

Capability declaration for Code Ingestion Agent.
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


CODE_INGESTION_AGENT_CAPABILITY = AgentCapability(
    agent_id="code_ingestion_agent",
    agent_name="Code Ingestion Agent",
    agent_type=AgentType.LEGACY_MODERNIZATION,

    description=(
        "Parses and catalogs legacy code. Creates structured representation of codebase for analysis."
    ),

    capabilities={
        "code_parsing",
        "ast_generation",
        "code_cataloging",
        "metadata_extraction"
    },

    supported_languages=[
        ""cobol"",
        ""fortran"",
        ""c"",
        ""java""
    ],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.CODE
    },

    output_types={
        "ast",
        "catalog",
        "metadata"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=False,
        kb_query_strategy=KBQueryStrategy.MINIMAL,
        kb_query_frequency=3,
        kb_query_triggers=[],
        max_kb_queries_per_task=10,
        enable_kb_caching=False,
        kb_cache_ttl_seconds=60
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
        "stage1",
        "etl",
        "parsing"
    
)


def get_code_ingestion_capability() -> AgentCapability:
    return CODE_INGESTION_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    CODE_INGESTION_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
