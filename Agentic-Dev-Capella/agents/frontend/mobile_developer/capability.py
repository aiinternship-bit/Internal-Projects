"""
agents/frontend/mobile_developer/capability.py

Capability declaration for Mobile Developer Agent.
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


MOBILE_DEVELOPER_AGENT_CAPABILITY = AgentCapability(
    agent_id="mobile_developer_agent",
    agent_name="Mobile Developer Agent",
    agent_type=AgentType.FRONTEND_ENGINEER,

    description=(
        "Specialized in mobile application development using React Native and Flutter. "
        "Handles platform-specific implementations, native modules, and cross-platform patterns."
    ),

    capabilities={
        "react_native_development",
        "flutter_development",
        "platform_specific_code",
        "native_modules",
        "mobile_navigation",
        "offline_sync",
        "push_notifications",
        "mobile_testing"
    },

    supported_languages=[
        "typescript",
        "javascript",
        "dart",
        "kotlin",
        "swift"
    ],

    supported_frameworks=[
        "react-native",
        "flutter",
        "expo",
        "react-navigation"
    ],

    supported_platforms=[
        "ios",
        "android",
        "mobile"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.IMAGE,
        InputModality.JSON,
        InputModality.DESIGN_FILE
    },

    output_types={
        "mobile_components",
        "typescript_code",
        "dart_code",
        "platform_code",
        "navigation_config",
        "tests"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,
        kb_query_triggers=["start", "error", "platform_issue", "checkpoint"],
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
        avg_validation_failures=0.5,
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
    tags=["frontend", "mobile", "react-native", "flutter", "cross-platform"]
)


def get_mobile_developer_capability() -> AgentCapability:
    return MOBILE_DEVELOPER_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    MOBILE_DEVELOPER_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
