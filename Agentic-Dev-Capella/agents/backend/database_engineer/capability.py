"""
agents/backend/database_engineer/capability.py

Capability declaration for Database Engineer Agent.
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


DATABASE_ENGINEER_CAPABILITY = AgentCapability(
    agent_id="database_engineer_agent",
    agent_name="Database Engineer Agent",
    agent_type=AgentType.DATABASE_ENGINEER,

    description=(
        "Designs database schemas, generates migration scripts, and optimizes queries. "
        "Supports relational (PostgreSQL, MySQL) and NoSQL (MongoDB, Redis) databases."
    ),

    capabilities={
        "schema_design",
        "migration_scripts",
        "query_optimization",
        "er_diagram_generation",
        "index_optimization",
        "normalization",
        "denormalization",
        "data_modeling"
    },

    supported_languages=[
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "redis"
    ],

    supported_frameworks=[
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "sqlalchemy",
        "alembic",
        "prisma",
        "typeorm"
    ],

    supported_platforms=[
        "cloud",
        "on-premise"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.JSON,
        InputModality.PDF
    },

    output_types={
        "schema",
        "migrations",
        "indexes",
        "er_diagram",
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
        avg_task_duration_minutes=12.0,
        p95_task_duration_minutes=25.0,
        success_rate=0.90,
        avg_validation_failures=0.5,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.10,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=12.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["backend", "database", "schema", "migration", "optimization"]
)


def get_database_engineer_capability() -> AgentCapability:
    return DATABASE_ENGINEER_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    DATABASE_ENGINEER_CAPABILITY.agent_id = vertex_ai_resource_id
