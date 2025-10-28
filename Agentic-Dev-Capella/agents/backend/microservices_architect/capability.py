"""
agents/backend/microservices_architect/capability.py

Capability declaration for Microservices Architect Agent.
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


MICROSERVICES_ARCHITECT_CAPABILITY = AgentCapability(
    agent_id="microservices_architect_agent",
    agent_name="Microservices Architect Agent",
    agent_type=AgentType.SOLUTION_ARCHITECT,

    description=(
        "Designs microservices architectures using advanced reasoning. "
        "Decomposes monoliths, designs API gateways, event-driven systems, and applies "
        "patterns like CQRS, Event Sourcing, and Saga for distributed systems."
    ),

    capabilities={
        "service_decomposition",
        "api_gateway_design",
        "event_driven_architecture",
        "cqrs_pattern",
        "event_sourcing",
        "saga_pattern",
        "circuit_breaker",
        "service_mesh_design",
        "bounded_context_identification",
        "domain_driven_design"
    },

    supported_languages=[
        "architecture",  # Architecture diagrams and documentation
        "yaml",
        "json"
    ],

    supported_frameworks=[
        "istio",
        "linkerd",
        "kong",
        "nginx",
        "kafka",
        "rabbitmq"
    ],

    supported_platforms=[
        "cloud",
        "kubernetes",
        "microservices"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.JSON,
        InputModality.PDF
    },

    output_types={
        "architecture_design",
        "service_definitions",
        "event_flows",
        "configuration",
        "diagrams",
        "documentation"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,
        kb_query_triggers=["start", "error", "validation_fail", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=25.0,  # Longer due to complex reasoning
        p95_task_duration_minutes=50.0,
        success_rate=0.85,
        avg_validation_failures=1.0,
        retry_rate=0.25
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.25,  # Higher due to reasoning model
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=2,  # Lower due to reasoning model resource requirements
    estimated_task_duration_minutes=25.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["backend", "architecture", "microservices", "distributed-systems", "ddd"]
)


def get_microservices_architect_capability() -> AgentCapability:
    return MICROSERVICES_ARCHITECT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    MICROSERVICES_ARCHITECT_CAPABILITY.agent_id = vertex_ai_resource_id
