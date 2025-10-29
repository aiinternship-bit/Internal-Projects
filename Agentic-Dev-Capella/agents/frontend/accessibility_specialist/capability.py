"""
agents/frontend/accessibility_specialist/capability.py

Capability declaration for Accessibility Specialist Agent.
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


ACCESSIBILITY_SPECIALIST_AGENT_CAPABILITY = AgentCapability(
    agent_id="accessibility_specialist_agent",
    agent_name="Accessibility Specialist Agent",
    agent_type=AgentType.FRONTEND_ENGINEER,

    description=(
        "Ensures WCAG compliance and accessibility best practices. Implements ARIA, keyboard navigation, and screen reader support."
    ),

    capabilities={
        "accessibility_audit",
        "wcag_compliance",
        "aria_implementation",
        "keyboard_navigation"
    },

    supported_languages=[
        ""typescript"",
        ""javascript""
    ],

    supported_frameworks=[
        ""react"",
        ""vue""
    ],

    supported_platforms=[
        ""web""
    ],

    input_modalities={
        InputModality.CODE,
        InputModality.TEXT
    },

    output_types={
        "accessible_code",
        "audit_report",
        "recommendations"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=12,
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
        "accessibility",
        "wcag"
    
)


def get_accessibility_specialist_capability() -> AgentCapability:
    return ACCESSIBILITY_SPECIALIST_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    ACCESSIBILITY_SPECIALIST_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
