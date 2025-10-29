"""
agents/stage3_cicd/security/supply_chain/capability.py

Capability declaration for Supply Chain Security Agent.
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


SUPPLY_CHAIN_SECURITY_AGENT_CAPABILITY = AgentCapability(
    agent_id="supply_chain_security_agent",
    agent_name="Supply Chain Security Agent",
    agent_type=AgentType.SECURITY_ENGINEER,

    description=(
        "Scans dependencies for vulnerabilities. Ensures supply chain security compliance."
    ),

    capabilities={
        "dependency_scanning",
        "vulnerability_detection",
        "sbom_generation",
        "license_checking"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.CODE,
        InputModality.JSON
    },

    output_types={
        "security_report",
        "vulnerabilities",
        "sbom"
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
        "stage3",
        "security",
        "supply_chain"
    
)


def get_supply_chain_security_capability() -> AgentCapability:
    return SUPPLY_CHAIN_SECURITY_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    SUPPLY_CHAIN_SECURITY_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
