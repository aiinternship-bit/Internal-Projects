"""
agents/orchestration/dynamic_orchestrator/capability.py

Capability declaration for Dynamic Orchestrator Agent.
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


DYNAMIC_ORCHESTRATOR_CAPABILITY = AgentCapability(
    agent_id="dynamic_orchestrator_agent",
    agent_name="Dynamic Orchestrator Agent",
    agent_type=AgentType.ORCHESTRATOR,

    description=(
        "Dynamic capability-based orchestrator that analyzes tasks from multimodal inputs, "
        "selects optimal agents based on capabilities, and coordinates parallel execution. "
        "Integrates TaskAnalyzer, AgentSelector, and ExecutionPlanner."
    ),

    capabilities={
        "dynamic_agent_selection",
        "capability_matching",
        "task_analysis",
        "execution_planning",
        "multimodal_input_processing",
        "parallel_coordination",
        "dag_scheduling",
        "resource_optimization"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[
        "vertex_ai",
        "cloud"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.IMAGE,
        InputModality.PDF,
        InputModality.VIDEO,
        InputModality.AUDIO,
        InputModality.DESIGN_FILE,
        InputModality.CODE,
        InputModality.JSON,
        InputModality.YAML
    },

    output_types={
        "execution_plan",
        "agent_assignments",
        "task_requirements",
        "orchestration_report",
        "metrics"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=8,
        kb_query_triggers=["start", "agent_selection", "error"],
        max_kb_queries_per_task=30,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=600
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=5.0,
        p95_task_duration_minutes=10.0,
        success_rate=0.95,
        avg_validation_failures=0.2,
        retry_rate=0.05
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.05,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=10,
    estimated_task_duration_minutes=5.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["orchestration", "dynamic", "ai-powered", "capability-based", "multimodal"]
)


def get_dynamic_orchestrator_capability() -> AgentCapability:
    return DYNAMIC_ORCHESTRATOR_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    DYNAMIC_ORCHESTRATOR_CAPABILITY.agent_id = vertex_ai_resource_id
