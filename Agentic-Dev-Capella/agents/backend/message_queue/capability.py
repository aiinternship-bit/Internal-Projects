"""
agents/backend/message_queue/capability.py

Capability declaration for Message Queue Agent.
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


MESSAGE_QUEUE_CAPABILITY = AgentCapability(
    agent_id="message_queue_agent",
    agent_name="Message Queue Agent",
    agent_type=AgentType.BACKEND_ENGINEER,

    description=(
        "Sets up message brokers and designs event schemas for messaging systems. "
        "Supports Kafka, RabbitMQ, Google Pub/Sub with Avro, Protobuf, and JSON Schema."
    ),

    capabilities={
        "kafka_setup",
        "rabbitmq_setup",
        "pubsub_setup",
        "event_schema_design",
        "producer_consumer_implementation",
        "schema_registry",
        "message_versioning",
        "dead_letter_queues"
    },

    supported_languages=[
        "python",
        "typescript",
        "go",
        "java"
    ],

    supported_frameworks=[
        "kafka",
        "rabbitmq",
        "google-pubsub",
        "amazon-sqs-sns",
        "schema-registry"
    ],

    supported_platforms=[
        "cloud",
        "on-premise",
        "hybrid"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON,
        InputModality.CODE,
        InputModality.YAML
    },

    output_types={
        "configuration",
        "producer_code",
        "consumer_code",
        "schema",
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
        avg_task_duration_minutes=10.0,
        p95_task_duration_minutes=20.0,
        success_rate=0.90,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.08,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=10.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["backend", "messaging", "kafka", "rabbitmq", "event-driven"]
)


def get_message_queue_capability() -> AgentCapability:
    return MESSAGE_QUEUE_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    MESSAGE_QUEUE_CAPABILITY.agent_id = vertex_ai_resource_id
