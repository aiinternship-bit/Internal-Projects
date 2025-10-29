"""
agents/stage2_development/qa_tester/capability.py

Capability declaration for Qa Tester Agent.
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


QA_TESTER_AGENT_CAPABILITY = AgentCapability(
    agent_id="qa_tester_agent",
    agent_name="Qa Tester Agent",
    agent_type=AgentType.QA_ENGINEER,

    description=(
        "Generates and runs comprehensive tests. Creates unit, integration, and E2E tests."
    ),

    capabilities={
        "test_generation",
        "test_execution",
        "test_reporting",
        "coverage_analysis"
    },

    supported_languages=[
        ""python"",
        ""typescript"",
        ""java""
    ],

    supported_frameworks=[
        ""pytest"",
        ""jest"",
        ""junit""
    ],

    supported_platforms=[],

    input_modalities={
        InputModality.CODE
    },

    output_types={
        "test_suite",
        "test_report",
        "coverage_report"
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
        "stage2",
        "testing",
        "qa"
    
)


def get_qa_tester_capability() -> AgentCapability:
    return QA_TESTER_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    QA_TESTER_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
