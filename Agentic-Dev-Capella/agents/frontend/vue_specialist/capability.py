"""
agents/frontend/vue_specialist/capability.py

Capability declaration for Vue Specialist Agent.
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


VUE_SPECIALIST_AGENT_CAPABILITY = AgentCapability(
    agent_id="vue_specialist_agent",
    agent_name="Vue Specialist Agent",
    agent_type=AgentType.FRONTEND_ENGINEER,

    description=(
        "Expert in Vue.js 3 ecosystem with deep knowledge of Composition API, Nuxt 3, and Pinia. "
        "Specialized in modern Vue development patterns and performance optimization."
    ),

    capabilities={
        "vue3_composition_api",
        "nuxt3_development",
        "pinia_state_management",
        "vue_router",
        "composables",
        "server_side_rendering",
        "component_architecture",
        "typescript_vue"
    },

    supported_languages=[
        "typescript",
        "javascript",
        "vue"
    ],

    supported_frameworks=[
        "vue3",
        "nuxt3",
        "pinia",
        "vite"
    ],

    supported_platforms=[
        "web",
        "ssr"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.JSON,
        InputModality.IMAGE
    },

    output_types={
        "vue_components",
        "nuxt_pages",
        "composables",
        "pinia_stores",
        "typescript_code",
        "tests"
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
        avg_task_duration_minutes=16.0,
        p95_task_duration_minutes=32.0,
        success_rate=0.91,
        avg_validation_failures=0.4,
        retry_rate=0.11
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.13,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=4,
    estimated_task_duration_minutes=16.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["frontend", "vue", "nuxt", "typescript", "ssr"]
)


def get_vue_specialist_capability() -> AgentCapability:
    return VUE_SPECIALIST_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    VUE_SPECIALIST_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
