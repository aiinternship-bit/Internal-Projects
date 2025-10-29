"""
agents/frontend/ui_developer/capability.py

Capability declaration for Ui Developer Agent.
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


UI_DEVELOPER_AGENT_CAPABILITY = AgentCapability(
    agent_id="ui_developer_agent",
    agent_name="Ui Developer Agent",
    agent_type=AgentType.FRONTEND_ENGINEER,

    description=(
        "Generates UI components from design specifications. Creates accessible, responsive interfaces."
    ),

    capabilities={
        "ui_component_generation",
        "responsive_design",
        "accessibility_implementation"
    },

    supported_languages=[
        ""typescript"",
        ""javascript"",
        ""html"",
        ""css""
    ],

    supported_frameworks=[
        ""react"",
        ""vue"",
        ""angular""
    ],

    supported_platforms=[
        ""web""
    ],

    input_modalities={
        InputModality.IMAGE,
        InputModality.JSON,
        InputModality.DESIGN_FILE
    },

    output_types={
        "ui_components",
        "styles",
        "markup"
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
        "frontend",
        "ui",
        "components"
    
)


def get_ui_developer_capability() -> AgentCapability:
    return UI_DEVELOPER_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    UI_DEVELOPER_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
