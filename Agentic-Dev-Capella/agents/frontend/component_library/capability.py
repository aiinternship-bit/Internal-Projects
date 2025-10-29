"""
agents/frontend/component_library/capability.py

Capability declaration for Component Library Agent.
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


COMPONENT_LIBRARY_AGENT_CAPABILITY = AgentCapability(
    agent_id="component_library_agent",
    agent_name="Component Library Agent",
    agent_type=AgentType.FRONTEND_ENGINEER,

    description=(
        "Expert in creating design system component libraries with Storybook documentation. "
        "Specialized in reusable component architecture, design tokens, and accessibility standards."
    ),

    capabilities={
        "design_system_components",
        "component_library_architecture",
        "storybook_documentation",
        "design_tokens",
        "component_variants",
        "css_in_js",
        "accessibility_standards",
        "tree_shaking",
        "typescript_components"
    },

    supported_languages=[
        "typescript",
        "javascript",
        "css",
        "json"
    ],

    supported_frameworks=[
        "react",
        "vue",
        "vite",
        "storybook",
        "styled-components",
        "emotion"
    ],

    supported_platforms=[
        "web",
        "npm_packages"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.JSON,
        InputModality.IMAGE
    },

    output_types={
        "component_library",
        "design_tokens",
        "storybook_stories",
        "component_code",
        "typescript_code",
        "documentation"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,
        kb_query_triggers=["start", "error", "pattern_needed", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=18.0,
        p95_task_duration_minutes=35.0,
        success_rate=0.89,
        avg_validation_failures=0.5,
        retry_rate=0.13
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.15,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=4,
    estimated_task_duration_minutes=18.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["frontend", "components", "design-system", "storybook", "accessibility"]
)


def get_component_library_capability() -> AgentCapability:
    return COMPONENT_LIBRARY_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    COMPONENT_LIBRARY_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
