"""
agents/stage1_etl/static_analysis/capability.py

Capability declaration for Static Analysis Agent.
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


STATIC_ANALYSIS_AGENT_CAPABILITY = AgentCapability(
    agent_id="static_analysis_agent",
    agent_name="Static Analysis Agent",
    agent_type=AgentType.LEGACY_MODERNIZATION,

    description=(
        "Performs static code analysis on legacy codebase. Identifies code quality, complexity, and technical debt."
    ),

    capabilities={
        "static_analysis",
        "complexity_calculation",
        "dependency_analysis",
        "quality_metrics"
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
        "analysis_report",
        "metrics",
        "dependencies"
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
        avg_task_duration_minutes=20.0,
        p95_task_duration_minutes=40.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.16,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=20.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "stage1",
        "etl",
        "analysis"
    
)


def get_static_analysis_capability() -> AgentCapability:
    return STATIC_ANALYSIS_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    STATIC_ANALYSIS_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
