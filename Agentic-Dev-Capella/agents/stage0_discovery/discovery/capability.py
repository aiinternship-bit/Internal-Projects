"""
agents/stage0_discovery/discovery/capability.py

Capability declaration for Discovery Agent.
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


DISCOVERY_AGENT_CAPABILITY = AgentCapability(
    agent_id="discovery_agent",
    agent_name="Discovery Agent",
    agent_type=AgentType.LEGACY_MODERNIZATION,

    description=(
        "Scans legacy codebase, identifies languages, frameworks, and creates file inventory. Entry point for modernization pipeline."
    ),

    capabilities={
        "legacy_code_scanning",
        "language_detection",
        "framework_identification",
        "file_inventory"
    },

    supported_languages=[
        ""cobol"",
        ""fortran"",
        ""c"",
        ""java"",
        ""python""
    ],

    supported_frameworks=[],

    supported_platforms=[
        ""mainframe"",
        ""on-premise""
    ],

    input_modalities={
        InputModality.CODE,
        InputModality.TEXT
    },

    output_types={
        "inventory",
        "metadata",
        "scan_report"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=False,
        kb_query_strategy=KBQueryStrategy.MINIMAL,
        kb_query_frequency=5,
        kb_query_triggers=[],
        max_kb_queries_per_task=10,
        enable_kb_caching=False,
        kb_cache_ttl_seconds=60
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
        "stage0",
        "discovery",
        "legacy"
    
)


def get_discovery_capability() -> AgentCapability:
    return DISCOVERY_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    DISCOVERY_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
