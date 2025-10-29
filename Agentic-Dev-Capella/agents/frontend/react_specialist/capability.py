"""
agents/frontend/react_specialist/capability.py

Capability declaration for React Specialist Agent.
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


REACT_SPECIALIST_AGENT_CAPABILITY = AgentCapability(
    agent_id="react_specialist_agent",
    agent_name="React Specialist Agent",
    agent_type=AgentType.FRONTEND_ENGINEER,

    description=(
        "Expert in React ecosystem with deep knowledge of advanced patterns, performance optimization, "
        "and best practices. Specialized in Next.js, state management, and React Server Components."
    ),

    capabilities={
        "advanced_react_patterns",
        "performance_optimization",
        "state_management",
        "nextjs_development",
        "react_server_components",
        "component_architecture",
        "hooks_patterns",
        "testing_strategies"
    },

    supported_languages=[
        "typescript",
        "javascript",
        "jsx",
        "tsx"
    ],

    supported_frameworks=[
        "react",
        "nextjs",
        "redux",
        "zustand",
        "react-query",
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
        "react_components",
        "typescript_code",
        "hooks",
        "state_management_code",
        "tests",
        "documentation"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=12,
        kb_query_triggers=["start", "error", "pattern_needed", "checkpoint"],
        max_kb_queries_per_task=60,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=18.0,
        p95_task_duration_minutes=35.0,
        success_rate=0.92,
        avg_validation_failures=0.4,
        retry_rate=0.10
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
    tags=["frontend", "react", "nextjs", "typescript", "performance"]
)


def get_react_specialist_capability() -> AgentCapability:
    return REACT_SPECIALIST_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    REACT_SPECIALIST_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
