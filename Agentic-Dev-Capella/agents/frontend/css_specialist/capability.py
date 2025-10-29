"""
agents/frontend/css_specialist/capability.py

Capability declaration for Css Specialist Agent.
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


CSS_SPECIALIST_AGENT_CAPABILITY = AgentCapability(
    agent_id="css_specialist_agent",
    agent_name="Css Specialist Agent",
    agent_type=AgentType.FRONTEND_ENGINEER,

    description=(
        "Specialized in CSS and styling. Implements design systems, animations, and responsive layouts."
    ),

    capabilities={
        "css_generation",
        "responsive_design",
        "animation",
        "design_system_implementation"
    },

    supported_languages=[
        ""css"",
        ""scss"",
        ""sass""
    ],

    supported_frameworks=[
        ""tailwind"",
        ""styled-components"",
        ""css-modules""
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
        "stylesheets",
        "design_tokens",
        "animations"
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
        "frontend",
        "css",
        "styling"
    
)


def get_css_specialist_capability() -> AgentCapability:
    return CSS_SPECIALIST_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    CSS_SPECIALIST_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
